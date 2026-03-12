import streamlit as st
import base64
import uuid
import datetime
import json
import os
import boto3
import requests
from openai import OpenAI
import anthropic
from dotenv import load_dotenv

# =========================
# ENV & CLIENTS
# =========================
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("BUCKET_NAME")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# =========================
# UI / SIDEBAR
# =========================
def inject_sidebar_branding(logo_path: str = "assets/logo_disc.png"):
    """Logo au-dessus de la navigation (CSS only), sans crop."""
    try:
        with open(logo_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()

        css = f"""
        <style>
        /* Header sidebar = zone logo */
        [data-testid="stSidebarHeader"] {{
            height: 170px;                 /* <-- hauteur réelle */
            padding: 0 !important;         /* <-- stop padding-top hack */
            margin: 0;
            background-image: url("data:image/png;base64,{encoded}");
            background-repeat: no-repeat;
            background-position: center center;
            background-size: contain;      /* <-- clé anti-crop */
            overflow: visible;             /* <-- au cas où */
        }}

        /* Séparateur / encadrement nav */
        [data-testid="stSidebarNav"] {{
            border-top: 1px solid rgba(49, 51, 63, 0.25);
            border-bottom: 1px solid rgba(49, 51, 63, 0.25);
            padding-top: 0.35rem;
            padding-bottom: 0.35rem;
            margin-top: 0.35rem;
            margin-bottom: 0.35rem;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

    except Exception as e:
        st.sidebar.warning(f"Logo non chargé : {e}")


def init_session():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

def render_pseudo_sidebar():
    if "pseudo_value" not in st.session_state:
        st.session_state["pseudo_value"] = ""

    def _sync_pseudo():
        st.session_state["pseudo_value"] = st.session_state["pseudo_widget"]

    st.sidebar.text_input(
        "Renseignez votre pseudo",
        key="pseudo_widget",
        value=st.session_state["pseudo_value"],
        on_change=_sync_pseudo,
    )

    return st.session_state["pseudo_value"]

# =========================
# LLM
# =========================
def call_llm(prompt: str, model: str, temperature: float, max_tokens: int, top_p: float) -> str:
    if model == "OpenAI":
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )
        return response.choices[0].message.content.strip()

    if model == "Mistral":
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "mistral-medium-latest",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
        }

        r = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()

    if model == "Claude":
        message = anthropic_client.messages.create(
            model="claude-opus-4-6",
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()

    return "Modèle non reconnu."


# =========================
# LOGGING
# =========================
def log_interaction(
    pseudo: str,
    exercice: str,
    tab: str,
    prompt: str,
    response: str,
    model: str,
    temperature: float,
    max_tokens: int,
    top_p: float,
):
    timestamp = datetime.datetime.utcnow().isoformat().replace(":", "-")
    filename = f"log_{st.session_state.session_id}_{timestamp}.json"

    log_data = {
        "timestamp": timestamp,
        "jour": datetime.datetime.now().strftime("%d/%m/%Y"),
        "session_id": st.session_state.session_id,
        "pseudo": pseudo,
        "exercice": exercice,
        "tab": tab,
        "modele": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "prompt": prompt,
        "reponse": response,
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False)

    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

    s3.upload_file(filename, BUCKET_NAME, filename)
    os.remove(filename)
