import streamlit as st
import base64
from PIL import Image
from contenu_promptfight import PROMPTFIGHT_CONTENT
from utils import (
    inject_sidebar_branding,
    render_pseudo_sidebar,
)

st.set_page_config(page_title="Apprendre à prompter", page_icon="💊", layout="wide")

inject_sidebar_branding()
render_pseudo_sidebar()

st.title("🧪 Expérimenter les *prompts* et le *prompt engineering*")

st.header("Bienvenue dans *Prompt Fighter* 👊")

st.markdown(
    """Cette application est un **bac à sable** permettant d'explorer le comportement des **LLM** (*Large Language Models*).
- L'interface vous permet d'effectuer des **demandes simples**, sur des données publiques et fictives, et d'observer la réponse des modèles LLM.
- L'application ne gère pas les **images** ni les **fichiers** à analyser (documents, PDF, etc.).
- Il n'y a **pas de discussion** (pas de conversation multi-tours) et **pas de mémorisation** d'un historique.
)


Comment utiliser l'application ? 
- Utilisez le menu de gauche pour sélectionner une page d'exercice, 
- Renseignez votre pseudo
- Sélectionnez un type de LLM (Mistral, Claude ou OpenAI)
- Modifiez éventuellement les paramètres des modèles
- Soumettez vos prompts et comparez les sorties.
"""
)