import streamlit as st
from contenu_promptfight import PROMPTFIGHT_CONTENT
from utils import (
    inject_sidebar_branding,
    init_session,
    call_llm,
    log_interaction,
    render_pseudo_sidebar,
)

def reset_ex1_tab1():
    st.session_state["ex1_prompt_tab1"] = ""
    st.session_state["ex1_response_tab1"] = ""

def reset_ex1_tab2():
    st.session_state["ex1_prompt_tab2"] = ""
    st.session_state["ex1_response_tab2"] = ""

st.set_page_config(
    page_title="Exercice 1 – Générer un support de communication",
    page_icon="🔐",
    layout="wide",
)

# --- Init UI / session
inject_sidebar_branding()
init_session()

# --- Sidebar controls
pseudo = render_pseudo_sidebar()

modele = st.sidebar.selectbox("Choix du modèle LLM", ["Mistral", "OpenAI"])
with st.sidebar.expander("⚙️ Réglages", expanded=False):
    temperature = st.slider("Température", 0.0, 1.0, 0.7, step=0.1)
    max_tokens = st.slider("Max tokens", 100, 2000, 1000, step=100)
    top_p = st.slider("Top-p", 0.0, 1.0, 1.0, step=0.1)

# --- Page content
st.header("🔍✅ Exercice 1 – Générer un support de communication")

tab1, tab2 = st.tabs(["Enoncé", "Conseils"])

with tab1:
    st.markdown(PROMPTFIGHT_CONTENT["ex1"]["enonce"])

    prompt_key = "ex1_prompt_tab1"
    resp_key = "ex1_response_tab1"

    prompt = st.text_area(
        "Écrivez ici votre prompt :",
        key=prompt_key,
        height=220,
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Soumettre la demande au LLM", key="ex1_send_tab1"):
            if not pseudo:
                st.warning("Merci de renseigner un pseudo dans la barre latérale.")
            elif not prompt.strip():
                st.warning("Merci d'écrire un prompt.")
            else:
                with st.spinner("En attente de la réponse..."):
                    response = call_llm(
                        prompt=prompt,
                        model=modele,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                    )
                    st.session_state[resp_key] = response

                    log_interaction(
                        pseudo=pseudo,
                        exercice="Ex.1",
                        tab="tab1",
                        prompt=prompt,
                        response=response,
                        model=modele,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                    )

    with col2:
        st.button("Réinitialiser", key="ex1_reset_tab1", on_click=reset_ex1_tab1)

    if resp_key in st.session_state and st.session_state[resp_key]:
        st.markdown("### Réponse de l'IA")
        st.markdown(
            f"""
            <div style="background-color:#e6ffe6;padding:10px;border-radius:5px;">
            {st.session_state[resp_key]}
            </div>
            """,
            unsafe_allow_html=True,
        )

with tab2:
    st.markdown(PROMPTFIGHT_CONTENT["ex1"]["enonce"])

    st.markdown("""L'objectif est d'obtenir une proposition qui :
- explique simplement la Data Integrity et éventuellement les concepts **ALCOA+**,  
- l'illustre avec **des exemples concrets** ou des **bonnes pratiques quotidiennes** d'application terrain (enregistrement en temps réel, pas de brouillons, corrections tracées, etc.),  
- évite le jargon réglementaire inutile, tout en restant **juste et conforme**.
""")

    with st.expander("📚 Conseils", expanded=False):
        st.markdown(PROMPTFIGHT_CONTENT["ex1"]["conseils"])

    prompt_key = "ex1_prompt_tab2"
    resp_key = "ex1_response_tab2"

    prompt = st.text_area(
        "Écrivez ici votre prompt :",
        key=prompt_key,
        height=220,
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Soumettre la demande au LLM", key="ex1_send_tab2"):
            if not pseudo:
                st.warning("Merci de renseigner un pseudo dans la barre latérale.")
            elif not prompt.strip():
                st.warning("Merci d'écrire un prompt.")
            else:
                with st.spinner("En attente de la réponse..."):
                    response = call_llm(
                        prompt=prompt,
                        model=modele,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                    )
                    st.session_state[resp_key] = response

                    log_interaction(
                        pseudo=pseudo,
                        exercice="Ex.1",
                        tab="tab2",
                        prompt=prompt,
                        response=response,
                        model=modele,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                    )

    with col2:
        st.button("Réinitialiser", key="ex1_reset_tab2", on_click=reset_ex1_tab2)

    if resp_key in st.session_state and st.session_state[resp_key]:
        st.markdown("### Réponse de l'IA")
        st.markdown(
            f"""
            <div style="background-color:#e6ffe6;padding:10px;border-radius:5px;">
            {st.session_state[resp_key]}
            </div>
            """,
            unsafe_allow_html=True,
        )
