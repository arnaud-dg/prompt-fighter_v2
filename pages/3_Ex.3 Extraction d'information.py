import streamlit as st
from contenu_promptfight import PROMPTFIGHT_CONTENT
from utils import (
    inject_sidebar_branding,
    init_session,
    call_llm,
    log_interaction,
    render_pseudo_sidebar,
)

def reset_ex3_tab1():
    st.session_state["ex3_prompt_tab1"] = ""
    st.session_state["ex3_response_tab1"] = ""

def reset_ex3_tab2():
    st.session_state["ex3_prompt_tab2"] = ""
    st.session_state["ex3_response_tab2"] = ""

st.set_page_config(
    page_title="Exercice 3 – Extraction d'informations",
    page_icon="⚠️",
    layout="wide",
)

inject_sidebar_branding()
init_session()

pseudo = render_pseudo_sidebar()

modele = st.sidebar.selectbox("Choix du modèle LLM", ["Mistral", "OpenAI"])
with st.sidebar.expander("⚙️ Réglages", expanded=False):
    temperature = st.slider("Température", 0.0, 1.0, 0.7, step=0.1)
    max_tokens = st.slider("Max tokens", 100, 2000, 1000, step=100)
    top_p = st.slider("Top-p", 0.0, 1.0, 1.0, step=0.1)

st.header("⚠️ Exercice 3 – Extraction d'informations d'un narratif")

tab1, tab2 = st.tabs(["Enoncé", "Conseils"])

with tab1:
    st.markdown(PROMPTFIGHT_CONTENT["ex3"]["enonce"])
    st.markdown("""
Voici le narratif de l'accident à analyser : 

Après avoir procédé à la soudure d'une cloison, un soudeur de 52 ans déplaçait son matériel de la cloison vers la citerne pour le ranger.
La citerne s'est mise tout à coup en rotation.
Surpris, le soudeur a été déséquilibré et est tombé à travers le trou d'homme d'une hauteur de 40 cm, sur ses pieds, entraînant un traumatisme à la cheville droite et des contusions aux genoux.
Il aurait actionné malencontreusement la citerne en appuyant sur le bouton de la commande filaire posée au sol sur la citerne.

En complément le service EHS vous a fourni des exemples d'accidents qu'il a déjà pu analyser :
""")
    with st.expander("📚 Exemples", expanded=False):
        st.markdown("""
Exemple 1 – Narratif :
Un opérateur de fabrication de 38 ans en contrat de professionnalisation était en phase de préparation du conditionnement de poudre de médicament en sachets.
Le procédé comprenait une étape de retrait de la charlotte de protection hygiénique présente en partie basse à l'orifice de déversement par gravité d'une cuve contenant la poudre.
L'opérateur avait levé la cuve au moyen d'une potence composée d'un mât rotatif fixé au sol et d'un tablier à fourches permettant la montée/descente de la cuve.
Il était à proximité de la cuve et du poste de commande lorsque la cuve de 900 kg a chuté sur lui.
Des collègues se sont précipités pour lui porter secours en soulevant la cuve au moyen d'un chariot élévateur et en plaçant des cales. L'opérateur est décédé.
(Constats et détails complémentaires non indispensables à l'extraction.)
Extraction attendue :
Age:38  | Métier:Opérateur | Symptomes:Ecrasement et décès | Cause:Chute d'une cuve de 900kg

---

Exemple 2 – Narratif :
La victime, monteur tôlier, âgé de 31 ans, devait, avec un autre salarié, effectuer le transfert du mano-détendeur d'un cadre à oxygène vide sur un cadre à oxygène plein.
Au moment du branchement du raccord liant la tuyauterie souple au détendeur, une violente déflagration se produit, des étincelles jaillissent du détendeur.
Les deux salariés sont brûlés au visage, aux bras et à l'abdomen.
Extraction attendue :
Age:31 | Métier:Monteur tôlier | Symptomes:Brulure au visage, bras et abdomen | Cause:Explosion au branchement du raccord

        """)

    prompt_key = "ex3_prompt_tab1"
    resp_key = "ex3_response_tab1"

    prompt = st.text_area(
        "Écrivez ici votre prompt :",
        key=prompt_key,
        height=220,
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Soumettre la demande au LLM", key="ex3_send_tab1"):
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
                        exercice="Ex.3",
                        tab="tab1",
                        prompt=prompt,
                        response=response,
                        model=modele,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                    )

    with col2:
        st.button("Réinitialiser", key="ex3_reset_tab1", on_click=reset_ex3_tab1)

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
    st.markdown(PROMPTFIGHT_CONTENT["ex3"]["enonce"])
    st.markdown("""
Voici le narratif de l'accident à analyser : 

Après avoir procédé à la soudure d'une cloison, un soudeur de 52 ans déplaçait son matériel de la cloison vers la citerne pour le ranger.
La citerne s'est mise tout à coup en rotation.
Surpris, le soudeur a été déséquilibré et est tombé à travers le trou d'homme d'une hauteur de 40 cm, sur ses pieds, entraînant un traumatisme à la cheville droite et des contusions aux genoux.
Il aurait actionné malencontreusement la citerne en appuyant sur le bouton de la commande filaire posée au sol sur la citerne.

En complément le service EHS vous a fourni des exemples d'accidents qu'il a déjà pu analyser :
""")
    with st.expander("📚 Exemples", expanded=False):
        st.markdown("""
Exemple 1 – Narratif :
Un opérateur de fabrication de 38 ans en contrat de professionnalisation était en phase de préparation du conditionnement de poudre de médicament en sachets.
Le procédé comprenait une étape de retrait de la charlotte de protection hygiénique présente en partie basse à l'orifice de déversement par gravité d'une cuve contenant la poudre.
L'opérateur avait levé la cuve au moyen d'une potence composée d'un mât rotatif fixé au sol et d'un tablier à fourches permettant la montée/descente de la cuve.
Il était à proximité de la cuve et du poste de commande lorsque la cuve de 900 kg a chuté sur lui.
Des collègues se sont précipités pour lui porter secours en soulevant la cuve au moyen d'un chariot élévateur et en plaçant des cales. L'opérateur est décédé.
(Constats et détails complémentaires non indispensables à l'extraction.)
Extraction attendue :
Age:38  | Métier:Opérateur | Symptomes:Ecrasement et décès | Cause:Chute d'une cuve de 900kg

---

Exemple 2 – Narratif :
La victime, monteur tôlier, âgé de 31 ans, devait, avec un autre salarié, effectuer le transfert du mano-détendeur d'un cadre à oxygène vide sur un cadre à oxygène plein.
Au moment du branchement du raccord liant la tuyauterie souple au détendeur, une violente déflagration se produit, des étincelles jaillissent du détendeur.
Les deux salariés sont brûlés au visage, aux bras et à l'abdomen.
Extraction attendue :
Age:31 | Métier:Monteur tôlier | Symptomes:Brulure au visage, bras et abdomen | Cause:Explosion au branchement du raccord

        """)

    with st.expander("📚 Conseils", expanded=False):
        st.markdown(PROMPTFIGHT_CONTENT["ex3"]["conseils"])

    prompt_key = "ex3_prompt_tab2"
    resp_key = "ex3_response_tab2"

    prompt = st.text_area(
        "Écrivez ici votre prompt :",
        key=prompt_key,
        height=220,
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Soumettre la demande au LLM", key="ex3_send_tab2"):
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
                        exercice="Ex.3",
                        tab="tab2",
                        prompt=prompt,
                        response=response,
                        model=modele,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                    )

    with col2:
        st.button("Réinitialiser", key="ex3_reset_tab2", on_click=reset_ex3_tab2)

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