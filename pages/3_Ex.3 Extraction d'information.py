import re
import streamlit as st
from contenu_promptfight import PROMPTFIGHT_CONTENT
from utils import (
    inject_sidebar_branding,
    init_session,
    call_llm,
    log_interaction,
    render_pseudo_sidebar,
)


# =========================
# Reset helpers
# =========================
def reset_ex3():
    keys_to_reset = [
        "ex3_prompt_improved",
        "ex3_response_generated",
        "ex3_prompt_evaluation",
        "ex3_eval_scores",
        "ex3_eval_note_finale",
    ]
    for key in keys_to_reset:
        st.session_state[key] = "" if key not in ["ex3_eval_scores"] else {}


# =========================
# Prompt d'évaluation
# =========================
def build_prompt_evaluation(user_prompt: str) -> str:
    return f"""
Tu es un évaluateur pédagogique spécialisé dans l'apprentissage du prompting en contexte professionnel.

Ta mission est d'évaluer la qualité du prompt suivant :

\"\"\"{user_prompt}\"\"\"

Évalue ce prompt selon les 5 critères suivants, chacun noté sur 5 :
- Clarté de la tâche
- Contexte fourni
- Utilisation d'exemples
- Respect de la typologie de sortie

Pour le critère "Utilisation d'exemples", tu dois évaluer si le prompt inclut :
- des exemples concrets illustrant le type d'extraction attendu (few-shot),

Pour le critère "Respect de la typologie de sortie", tu dois évaluer si le prompt inclut :
- des exemples suffisamment variés et représentatifs,
- une structure d'exemple claire et réutilisable par le modèle.

Règles :
- Sois strict mais juste.
- Base-toi uniquement sur la qualité du prompt, pas sur la qualité potentielle du modèle.
- Donne une note entière entre 0 et 5 pour chaque critère.
- Calcule ensuite une note finale sur 20.
- Pour chacun des 4 critères, ajoute un court commentaire pédagogique.
- Ne note pas la réponse produite, seulement le prompt lui-même.
- Reste pédagogique, clair et concret.

Présente impérativement la réponse sous cette forme exacte :

Clarté de la tâche : X/5
Commentaire : ...

Contexte fourni : X/5
Commentaire : ...

Utilisation d'exemples : X/5
Commentaire : ...

Respect de la typologie de sortie : X/5
Commentaire : ...

Note finale : X/20
"""


# =========================
# Parsing de l'évaluation
# =========================
def parse_evaluation(text: str):
    if not text:
        return {}, None

    patterns = {
        "Clarté de la tâche": r"Clarté de la tâche\s*:\s*(\d+)\s*/\s*5",
        "Contexte fourni": r"Contexte fourni\s*:\s*(\d+)\s*/\s*5",
        "Utilisation d'exemples": r"Utilisation d'exemples\s*:\s*(\d+)\s*/\s*5",
        "Respect de la typologie de sortie": r"Respect de la typologie de sortie\s*:\s*(\d+)\s*/\s*5",
    }

    scores = {}
    for label, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            scores[label] = int(match.group(1))

    note_match = re.search(r"Note finale\s*:\s*(\d+)\s*/\s*20", text, re.IGNORECASE)
    note_finale = int(note_match.group(1)) if note_match else None

    return scores, note_finale


# =========================
# Helpers UI
# =========================
def score_color(score: int, maximum: int = 4):
    ratio = score / maximum
    if ratio >= 0.8:
        return "#d4edda", "#155724", "#28a745"
    elif ratio >= 0.5:
        return "#fff3cd", "#856404", "#ffc107"
    else:
        return "#f8d7da", "#721c24", "#dc3545"


def note_color(note: int, maximum: int = 20):
    ratio = note / maximum
    if ratio >= 0.8:
        return "#d4edda", "#155724", "#28a745"
    elif ratio >= 0.5:
        return "#fff3cd", "#856404", "#ffc107"
    else:
        return "#f8d7da", "#721c24", "#dc3545"


def render_score_card(title: str, score: int, maximum: int = 4):
    bg, fg, border = score_color(score, maximum)
    st.markdown(
        f"""
        <div style="
            background:{bg};
            color:{fg};
            border-left:6px solid {border};
            padding:14px 16px;
            border-radius:12px;
            min-height:110px;
            display:flex;
            flex-direction:column;
            justify-content:space-between;
            box-shadow:0 2px 8px rgba(0,0,0,0.04);
            margin-bottom:12px;
        ">
            <div style="font-size:0.95rem;font-weight:600;line-height:1.3;">{title}</div>
            <div style="font-size:2rem;font-weight:800;margin-top:10px;">{score}/{maximum}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_note_card(note: int, maximum: int = 20):
    bg, fg, border = note_color(note, maximum)
    st.markdown(
        f"""
        <div style="
            background:{bg};
            color:{fg};
            border:2px solid {border};
            padding:22px 20px;
            border-radius:16px;
            text-align:center;
            box-shadow:0 4px 14px rgba(0,0,0,0.06);
            margin-bottom:12px;
        ">
            <div style="font-size:1rem;font-weight:600;opacity:0.9;">Note finale</div>
            <div style="font-size:3rem;font-weight:900;line-height:1.1;margin-top:8px;">{note}/{maximum}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# Page config
# =========================
st.set_page_config(
    page_title="Exercice 3 – Extraction d'informations",
    page_icon="⚠️",
    layout="wide",
)

# =========================
# Style léger
# =========================
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        max-width: 900px;
    }
    div[data-testid="stTextArea"] textarea {
        font-size: 0.96rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# Init UI / session
# =========================
inject_sidebar_branding()
init_session()

# =========================
# Sidebar controls
# =========================
pseudo = render_pseudo_sidebar()

modele = st.sidebar.selectbox("Choix du modèle LLM", ["Mistral", "OpenAI", "Claude"])

temperature = 0.7
max_tokens = 1000
top_p = 1.0
# with st.sidebar.expander("⚙️ Réglages", expanded=False):
#     temperature = st.slider("Température", 0.0, 1.0, 0.7, step=0.1)
#     max_tokens = st.slider("Max tokens", 100, 2000, 1000, step=100)
#     top_p = st.slider("Top-p", 0.0, 1.0, 1.0, step=0.1)

# =========================
# Page content
# =========================
st.header("⚠️ Ex.3 – Réalisation de tâches spécifiques")

st.markdown("""
### Contexte

Le service EHS fais appel à vous car il a besoin de support pour analyser, de façon reproductible et systématique, des narratifs d'accidentologie et en extraire un certains nombre d'informations, telles que :

- L'âge de la victime
- Son métier
- Les symptômes observés
- La cause principale de l'accident (Root-cause)
Ces données vont servir à alimenter automatiquement un tableau de bord de suivi de l'accidentologie. Il est donc important que l'on ne retrouve que ces informations

Voici le narratif de l'accident à analyser :

> Après avoir procédé à la soudure d'une cloison, un soudeur de 52 ans déplaçait son matériel de la cloison vers la citerne pour le ranger. La citerne s'est mise tout à coup en rotation. Surpris, le soudeur a été déséquilibré et est tombé à travers le trou d'homme d'une hauteur de 40 cm, sur ses pieds, entraînant un traumatisme à la cheville droite et des contusions aux genoux. Il aurait actionné malencontreusement la citerne en appuyant sur le bouton de la commande filaire posée au sol sur la citerne.
""")

with st.expander("📚 Exemples de format attendu", expanded=False):
    st.markdown("""
En complément le service EHS vous a fourni des exemples d'accidents qu'il a déjà pu analyser :

Exemple 1 – Narratif : Un opérateur de fabrication de 38 ans en contrat de professionnalisation était en phase de préparation du conditionnement de poudre de médicament en sachets. Le procédé comprenait une étape de retrait de la charlotte de protection hygiénique présente en partie basse à l'orifice de déversement par gravité d'une cuve contenant la poudre. L'opérateur avait levé la cuve au moyen d'une potence composée d'un mât rotatif fixé au sol et d'un tablier à fourches permettant la montée/descente de la cuve. Il était à proximité de la cuve et du poste de commande lorsque la cuve de 900 kg a chuté sur lui. Des collègues se sont précipités pour lui porter secours en soulevant la cuve au moyen d'un chariot élévateur et en plaçant des cales. L'opérateur est décédé. (Constats et détails complémentaires non indispensables à l'extraction.) Extraction attendue : Age:38 | Métier:Opérateur | Symptomes:Ecrasement et décès | Cause:Chute d'une cuve de 900kg

Exemple 2 – Narratif : La victime, monteur tôlier, âgé de 31 ans, devait, avec un autre salarié, effectuer le transfert du mano-détendeur d'un cadre à oxygène vide sur un cadre à oxygène plein. Au moment du branchement du raccord liant la tuyauterie souple au détendeur, une violente déflagration se produit, des étincelles jaillissent du détendeur. Les deux salariés sont brûlés au visage, aux bras et à l'abdomen. Extraction attendue : Age:31 | Métier:Monteur tôlier | Symptomes:Brulure au visage, bras et abdomen | Cause:Explosion au branchement du raccord
    """)

st.markdown(
    """
### Votre mission : 

1. Essayez de construire un prompt qui donne **de façon répétable**, les 4 informations souhaitées séparées par le caractère "|".
2. **Impératif** : Afin d'alimenter un tableau de bord automatique. Le prompt ne doit rien fournir d'autres que ces 4 informations.
""")

st.subheader("✍️ Réécriture du prompt")

improved_prompt = st.text_area(
    "Réécrivez ici un prompt amélioré :",
    key="ex3_prompt_improved",
    height=240,
)

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("🚀 Soumettre la demande au LLM", key="ex3_send"):
        if not pseudo:
            st.warning("Merci de renseigner un pseudo dans la barre latérale.")
        elif not improved_prompt.strip():
            st.warning("Merci de rédiger un prompt amélioré.")
        else:
            with st.spinner("Génération de la réponse puis évaluation du prompt..."):
                # 1er appel LLM : génération
                generated_response = call_llm(
                    prompt=improved_prompt,
                    model=modele,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                )

                st.session_state["ex3_response_generated"] = generated_response

                # 2e appel LLM : évaluation du prompt
                evaluation_prompt = build_prompt_evaluation(improved_prompt)

                prompt_evaluation = call_llm(
                    prompt=evaluation_prompt,
                    model=modele,
                    temperature=0.2,
                    max_tokens=900,
                    top_p=1.0,
                )

                st.session_state["ex3_prompt_evaluation"] = prompt_evaluation

                scores, note_finale = parse_evaluation(prompt_evaluation)
                st.session_state["ex3_eval_scores"] = scores
                st.session_state["ex3_eval_note_finale"] = note_finale if note_finale is not None else ""

                log_interaction(
                    pseudo=pseudo,
                    exercice="Ex.3",
                    tab="extraction_info",
                    prompt=improved_prompt,
                    response=f"[REPONSE GENEREE]\n{generated_response}\n\n[EVALUATION DU PROMPT]\n{prompt_evaluation}",
                    model=modele,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                )

with col_btn2:
    st.button("♻️ Réinitialiser", key="ex3_reset", on_click=reset_ex3)

# =========================
# Affichage des résultats
# =========================
if st.session_state.get("ex3_response_generated"):
    st.markdown("---")
    st.subheader("Réponse générée par l'IA")
    st.markdown(
        f"""
        <div style="
            background-color:#f8fff8;
            padding:18px;
            border-radius:12px;
            border:1px solid #d6ead8;
            box-shadow:0 2px 8px rgba(0,0,0,0.04);
        ">
        {st.session_state["ex3_response_generated"]}
        </div>
        """,
        unsafe_allow_html=True,
    )

if st.session_state.get("ex3_prompt_evaluation"):
    st.markdown("---")
    st.subheader("Évaluation du prompt")

    note_finale = st.session_state.get("ex3_eval_note_finale")
    scores = st.session_state.get("ex3_eval_scores", {})
    evaluation_text = st.session_state.get("ex3_prompt_evaluation", "")

    if isinstance(note_finale, int):
        render_note_card(note_finale)

    for label in [
        "Clarté de la tâche",
        "Contexte métier",
        "Définition du public cible",
        "Respect de la typologie de sortie "
    ]:
        if label in scores:
            render_score_card(label, scores[label], maximum=4)

    if evaluation_text:
        st.markdown(
            f"""
            <div style="
                background-color:#f6f8ff;
                padding:16px;
                border-radius:12px;
                border:1px solid #d9e2ff;
                white-space: pre-wrap;
                box-shadow:0 2px 8px rgba(0,0,0,0.04);
            ">
            {evaluation_text}
            </div>
            """,
            unsafe_allow_html=True,
        )
