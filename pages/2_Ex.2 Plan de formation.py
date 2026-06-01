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
def reset_ex2():
    keys_to_reset = [
        "ex2_prompt_improved",
        "ex2_response_generated",
        "ex2_prompt_evaluation",
        "ex2_eval_scores",
        "ex2_eval_note_finale",
    ]
    for key in keys_to_reset:
        st.session_state[key] = "" if key not in ["ex2_eval_scores"] else {}


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
- Contexte métier
- Définition du public cible
- Précision du format de sortie

Pour le critère "Précision du format de sortie", tu dois évaluer si le prompt précise clairement :
- le type de sortie attendu (par exemple : tableau, liste, plan, matrice),
- le nombre de réponses souhaitées,
- les colonnes du tableau ou les champs attendus si un tableau est demandé.

Règles :
- Sois strict mais juste.
- Base-toi uniquement sur la qualité du prompt, pas sur la qualité potentielle du modèle.
- Donne une note entière entre 0 et 5 pour chaque critère.
- Calcule ensuite une note finale sur 20.
- Pour chacun des ' critères, ajoute un court commentaire pédagogique.
- Ne note pas la réponse produite, seulement le prompt lui-même.
- Reste pédagogique, clair et concret.

Présente impérativement la réponse sous cette forme exacte :

Clarté de la tâche : X/5
Commentaire : ...

Contexte métier : X/5
Commentaire : ...

Définition du public cible : X/5
Commentaire : ...

Précision du format de sortie : X/5
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
        "Contexte métier": r"Contexte métier\s*:\s*(\d+)\s*/\s*5",
        "Définition du public cible": r"Définition du public cible\s*:\s*(\d+)\s*/\s*5",
        "Précision du format de sortie": r"Précision du format de sortie\s*:\s*(\d+)\s*/\s*5",
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
def score_color(score: int, maximum: int = 5):
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
    page_title="Exercice 2 – Plan de formation",
    page_icon="🧼",
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

modele = st.sidebar.selectbox("Choix du modèle LLM", ["Mistral_1", "Mistral_2", "Mistral_3", "Mistral_4", "OpenAI_1"])

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
st.header("🎓 Ex.2 – Le format de sortie")

st.markdown(
    """
### Contexte

Votre département Ressources Humaines vous sollicite afin de construire un plan de développement lié à la validation de nettoyage. 

L'idée est leur fournir un premier support de réflexion permettant d'alimenter un programme contenant différentes options de formation. Cela leur permettra d'évaluer les besoins de formation et de rechercher des prestataires adaptés. 

Rédigez un prompt afin de générer un programme de formation structuré sur les validations de nettoyage, adapté aux interlocuteurs RH qui ne sont absolument pas spécialistes techniques.

> **« Crée-moi un programme de formation sur la validation de nettoyage pour un public RH. »**

La réponse est disponible ci-dessous : 
""")

with st.expander("Réponse", expanded=False):
    st.markdown("""
Former un public RH à la validation de nettoyage est un exercice délicat, car le sujet est très GMP / production / qualité. Il faut donc éviter une approche trop technique et orienter la formation vers :
- compréhension des enjeux réglementaires
- impacts sur l'organisation et les compétences
- responsabilités RH (formation, habilitation, documentation, audits, gestion des écarts)
- culture qualité et conformité
Je te propose un programme structuré sur 1 journée (7 h), adapté à un public RH en industrie pharmaceutique / cosmétique / DM / agro.

🎓 Formation : Validation de nettoyage – rôle des RH en environnement GMP
**Public cible**
Professionnels RH, responsables formation, HRBP, responsables conformité ou toute fonction RH travaillant en environnement réglementé (pharmaceutique, cosmétique, dispositifs médicaux, agroalimentaire).

**Objectifs**
Comprendre les principes de la validation de nettoyage et identifier les responsabilités des RH dans la conformité GMP, la gestion des compétences et la préparation aux audits.

**Durée**

1 journée – 7 heures

**Module 1 — Contexte réglementaire et enjeux de conformité**

- Principes des GMP / BPF et rôle des autorités (ANSM, EMA, FDA)
- Notion de contamination et risques pour le patient / produit
- Importance de la traçabilité et de la documentation
- Place des compétences et de la formation dans la conformité

**Module 2 — Principes de la validation de nettoyage**

- Objectif de la validation de nettoyage et prévention des contaminations croisées
- Différence entre nettoyage de routine et nettoyage validé
- Notion de limites, worst case et acceptation
- Rôle des opérateurs, de la qualité et de la production

**Module 3 — Responsabilités des RH en environnement GMP**

- Gestion des formations obligatoires et recyclages
- Habilitation du personnel et suivi des compétences
- Gestion documentaire des dossiers formation
- Gestion des écarts liés au facteur humain

**Module 4 — Audits, inspections et organisation RH conforme**

- Attentes des inspecteurs concernant la formation du personnel
- Vérification des habilitations et de la traçabilité
- Bonnes pratiques d'organisation RH en environnement GMP
- Cas pratique : non-conformité liée à une formation manquante

Résultat attendu
À l'issue de la formation, les participants comprennent leur rôle dans la conformité GMP et savent structurer la gestion des compétences pour répondre aux exigences réglementaires, notamment dans le cadre de la validation de nettoyage.             
""")

st.markdown(
    """
### Analyse du résultat

Que pensez-vous du résultat produit ? 

Votre mission : 
1. **Modifiez le prompt en améliorant son contexte** afin que ce dernier propose différentes alternatives de formation permettant de sélectionner les modules souhaités ;
2. Conseil : Un format de sortie trop littéral n'est pas adapté à cet exercice. **Essayez de construire un prompt précisant le format de sortie**. Le format de sortie de type tableau peut-être toute à fait indiqué pour l'exercice ;
"""
)

st.subheader("✍️ Réécriture du prompt")

improved_prompt = st.text_area(
    "Réécrivez ici un prompt amélioré :",
    key="ex2_prompt_improved",
    height=240,
)

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("🚀 Soumettre la demande au LLM", key="ex2_send"):
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

                st.session_state["ex2_response_generated"] = generated_response

                # 2e appel LLM : évaluation du prompt
                evaluation_prompt = build_prompt_evaluation(improved_prompt)

                prompt_evaluation = call_llm(
                    prompt=evaluation_prompt,
                    model=modele,
                    temperature=0.2,
                    max_tokens=900,
                    top_p=1.0,
                )

                st.session_state["ex2_prompt_evaluation"] = prompt_evaluation

                scores, note_finale = parse_evaluation(prompt_evaluation)
                st.session_state["ex2_eval_scores"] = scores
                st.session_state["ex2_eval_note_finale"] = note_finale if note_finale is not None else ""

                log_interaction(
                    pseudo=pseudo,
                    exercice="Ex.2",
                    tab="format_sortie",
                    prompt=improved_prompt,
                    response=f"[REPONSE GENEREE]\n{generated_response}\n\n[EVALUATION DU PROMPT]\n{prompt_evaluation}",
                    model=modele,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                )

with col_btn2:
    st.button("♻️ Réinitialiser", key="ex2_reset", on_click=reset_ex2)

# =========================
# Affichage des résultats
# =========================
if st.session_state.get("ex2_response_generated"):
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
        {st.session_state["ex2_response_generated"]}
        </div>
        """,
        unsafe_allow_html=True,
    )

if st.session_state.get("ex2_prompt_evaluation"):
    st.markdown("---")
    st.subheader("Évaluation du prompt")

    note_finale = st.session_state.get("ex2_eval_note_finale")
    scores = st.session_state.get("ex2_eval_scores", {})
    evaluation_text = st.session_state.get("ex2_prompt_evaluation", "")

    if isinstance(note_finale, int):
        render_note_card(note_finale)

    for label in [
        "Clarté de la tâche",
        "Contexte métier",
        "Définition du public cible",
        "Format demandé",
        "Précision du format de sortie",
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