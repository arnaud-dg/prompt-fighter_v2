import re
import markdown as md_lib
import streamlit as st
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
def reset_ex1():
    keys_to_reset = [
        "ex1_prompt_improved",
        "ex1_response_generated",
        "ex1_prompt_evaluation",
        "ex1_eval_scores",
        "ex1_eval_note_finale",
    ]
    for key in keys_to_reset:
        st.session_state[key] = "" if key not in ["ex1_eval_scores"] else {}


# =========================
# Prompt d'évaluation
# =========================
def build_prompt_evaluation(user_prompt: str) -> str:
    return f"""
Tu es un évaluateur pédagogique spécialisé dans l’apprentissage du prompting en contexte professionnel.

Ta mission est d’évaluer la qualité du prompt suivant :

\"\"\"{user_prompt}\"\"\"

Évalue ce prompt selon les 4 critères suivants, chacun noté sur 5 :
- Clarté de la tâche
- Contexte métier
- Définition du public cible
- Format demandé

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

Contexte métier : X/5
Commentaire : ...

Définition du public cible : X/5
Commentaire : ...

Format demandé : X/5
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
        "Format demandé": r"Format demandé\s*:\s*(\d+)\s*/\s*5",
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


def render_score_card(title: str, score: int, maximum: int = 5):
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
    page_title="Exercice 1 – Diagnostiquer et améliorer un prompt",
    page_icon="🧠",
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
st.header("🔍 Ex.1 – L'anatomie d'un bon prompt")

st.markdown(
    """
### Contexte

Un de vos collègues, responsable assurance qualité sur un site de production pharmaceutique souhaite utiliser une **IA générative** pour gagner du temps dans la création de supports de communication internes.

Sa mission est de préparer un support de communication pour expliquer les concepts principaux de la **Data Integrity** aux **opérateurs du site**.

Pour cela, il a soumis à l'IA interne à l'entreprise le prompt suivant :

> **« Crée-moi s'il te plait un support de com sur la data integrity. »**

La réponse est disponible ci-dessous : 
""")

with st.expander("Réponse", expanded=False):
    st.markdown("""
Support de Communication : L'Intégrité des Données
- **1. Qu'est-ce que l'Intégrité des Données ?**
L'intégrité des données fait référence à la précision, la cohérence et la fiabilité des données tout au long de leur cycle de vie. Elle est essentielle pour garantir que les informations utilisées par l'organisation sont correctes et dignes de confiance.
- **2. Pourquoi est-ce Important ?**
Prise de décision éclairée : Des données fiables permettent aux entreprises de prendre des décisions stratégiques informées.
Conformité réglementaire : Certaines industries sont soumises à des réglementations strictes en matière de gestion des données.
Protection de la réputation : Les erreurs de données peuvent nuire à la confiance des clients et à l'image de marque de l'entreprise.
- **3. Types d'Intégrité des Données**
Intégrité physique : Protège les données contre les altérations non autorisées par des méthodes physiques (ex : sauvegardes).
Intégrité logique : Assure que les données sont cohérentes et conformes aux contraintes (ex : clés primaires en base de données).
Intégrité référentielle : Garantit que les relations entre les tables de données sont maintenues (ex : clé étrangère).
- **4. Menaces à l'Intégrité des Données**
Erreurs humaines : Saisie incorrecte ou mauvaise manipulation des données.
Attaques malveillantes : Piratages et cyberattaques visant à manipuler les données.
Pannes systémiques : Défaillances techniques ou logiciels causant des pertes de données.
- **5. Bonnes Pratiques pour Maintenir l'Intégrité des Données**
Validation des données : Mettre en place des contrôles pour vérifier l'exactitude des entrées de données.
Sauvegardes régulières : Assurer des sauvegardes fréquentes pour éviter la perte de données.
Accès restreint : Limiter l'accès aux informations sensibles pour minimiser les risques de manipulation.
Audit régulier : Effectuer des audits pour vérifier la qualité et la conformité des données.
- **6. Outils pour Assurer l'Intégrité des Données**
Systèmes de gestion de base de données (SGBD) : Utiliser des SGBD avec des fonctionnalités robustes d'intégrité des données.
Logiciels de nettoyage de données : Adopter des outils pour nettoyer et valider les données.
Solutions de surveillance : Mettre en place des outils qui surveillent en temps réel l'intégrité des données.
- **7. Conclusion**
L'intégrité des données est cruciale dans un environnement numérique en constante évolution. Mettre en œuvre des stratégies robustes pour maintenir cette intégrité est essentiel pour assurer la continuité des affaires et la confiance des clients.
""")

st.markdown(
    """
### Analyse du résultat

Que pensez-vous du résultat produit ? Quel en est l'origine ?

Votre mission : Vous devez aider votre collègue à :
1. **Expliquez à votre collègue** pourquoi son prompt est trop faible ;
2. **Identifier les risques** associés à un prompt aussi vague ;
3. **Réécrire un prompt plus efficace** pour obtenir un résultat plus clair, plus concret et mieux adapté aux opérateurs et techniciens.
"""
)

# with st.expander("💡 Aide : que peut-on améliorer dans un prompt ?", expanded=False):
#     st.markdown(
#         """
# Un prompt est généralement plus efficace lorsqu’il précise :

# - **la tâche** à réaliser ;
# - **le contexte métier** ;
# - **le public cible** ;
# - **le format attendu** ;
# - **le niveau de langage** ;
# - **les exemples concrets** à intégrer ;
# - **les contraintes de longueur ou de style**.
# """
#     )

st.subheader("✍️ Réécriture du prompt")

improved_prompt = st.text_area(
    "Aidez votre collègue à écrire une version améliorée de son prompt :",
    key="ex1_prompt_improved",
    height=260
)

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("🚀 Soumettre la demande au LLM", key="ex1_send"):
        if not pseudo:
            st.warning("Merci de renseigner un pseudo dans la barre latérale.")
        elif not improved_prompt.strip():
            st.warning("Merci de rédiger un prompt amélioré.")
        else:
            with st.spinner("Génération de la réponse puis évaluation du prompt..."):
                # 1er appel LLM : génération de la réponse
                generated_response = call_llm(
                    prompt=improved_prompt,
                    model=modele,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                )

                st.session_state["ex1_response_generated"] = generated_response

                # 2e appel LLM : évaluation du prompt lui-même
                evaluation_prompt = build_prompt_evaluation(improved_prompt)

                prompt_evaluation = call_llm(
                    prompt=evaluation_prompt,
                    model=modele,
                    temperature=0.2,
                    max_tokens=800,
                    top_p=1.0,
                )

                st.session_state["ex1_prompt_evaluation"] = prompt_evaluation

                scores, note_finale = parse_evaluation(prompt_evaluation)
                st.session_state["ex1_eval_scores"] = scores
                st.session_state["ex1_eval_note_finale"] = note_finale if note_finale is not None else ""

                log_interaction(
                    pseudo=pseudo,
                    exercice="Ex.1",
                    tab="diagnostic_prompt",
                    prompt=improved_prompt,
                    response=f"[REPONSE GENEREE]\n{generated_response}\n\n[EVALUATION DU PROMPT]\n{prompt_evaluation}",
                    model=modele,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                )

with col_btn2:
    st.button("♻️ Réinitialiser", key="ex1_reset", on_click=reset_ex1)

# =========================
# Affichage des résultats
# =========================
if st.session_state.get("ex1_response_generated"):
    st.markdown("---")
    st.subheader("Réponse générée par l’IA")
    st.markdown(
        f"""
        <div style="
            background-color:#f8fff8;
            padding:18px;
            border-radius:12px;
            border:1px solid #d6ead8;
            box-shadow:0 2px 8px rgba(0,0,0,0.04);
        ">
        {md_lib.markdown(st.session_state["ex1_response_generated"])}
        </div>
        """,
        unsafe_allow_html=True,
    )

if st.session_state.get("ex1_prompt_evaluation"):
    st.markdown("---")
    st.subheader("Évaluation du prompt")

    note_finale = st.session_state.get("ex1_eval_note_finale")
    scores = st.session_state.get("ex1_eval_scores", {})
    evaluation_text = st.session_state.get("ex1_prompt_evaluation", "")

    if isinstance(note_finale, int):
        render_note_card(note_finale)

    for label in [
        "Clarté de la tâche",
        "Contexte métier",
        "Définition du public cible",
        "Format demandé",
    ]:
        if label in scores:
            render_score_card(label, scores[label])

    if evaluation_text:
        st.markdown(
            f"""
            <div style="
                background-color:#f6f8ff;
                padding:16px;
                border-radius:12px;
                border:1px solid #d9e2ff;
                box-shadow:0 2px 8px rgba(0,0,0,0.04);
            ">
            {md_lib.markdown(evaluation_text)}
            </div>
            """,
            unsafe_allow_html=True,
        )

# st.markdown("---")
# st.info(
#     "L’évaluation affichée porte uniquement sur la qualité du prompt rédigé, et non sur la qualité de la réponse générée."
# )