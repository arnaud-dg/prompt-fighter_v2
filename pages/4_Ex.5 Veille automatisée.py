import streamlit as st
from utils import inject_sidebar_branding, init_session

st.set_page_config(
    page_title="Ex.5 Veille automatisée",
    page_icon="🛰️",
    layout="wide",
)

inject_sidebar_branding()
init_session()

# --- Sidebar : pseudo persistant
if "pseudo_value" not in st.session_state:
    st.session_state["pseudo_value"] = ""

def _sync_pseudo():
    st.session_state["pseudo_value"] = st.session_state["pseudo_widget"]

pseudo = st.sidebar.text_input(
    "Renseignez votre pseudo",
    key="pseudo_widget",
    value=st.session_state["pseudo_value"],
    on_change=_sync_pseudo,
)

# Source de vérité (rémanente)
pseudo = st.session_state["pseudo_value"]

st.header("🛰️ Ex.5 Veille automatisée")

st.markdown(
    """
    <div style="text-align:center; margin-top:120px; font-size:28px;">
        🚧 <strong>Page en construction</strong> 🚧
    </div>
    """,
    unsafe_allow_html=True,
)
