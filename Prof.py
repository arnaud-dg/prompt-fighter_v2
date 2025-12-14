import streamlit as st
import boto3
import os
import datetime
import json
import pandas as pd
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Configuration AWS
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("BUCKET_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

client = OpenAI(api_key=OPENAI_API_KEY)

st.set_page_config(
    page_title="Dashboard Prof",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Logo dans la sidebar
logo = Image.open("assets/logo_disc_prof.png")
with st.sidebar:
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st.image(logo, width=250)

st.sidebar.markdown("---")

# Filtres : date, tab
date_filter = st.sidebar.text_input("🗕️ Date du jour", datetime.datetime.now().strftime("%d/%m/%Y"))

tab_filter = st.sidebar.selectbox("🧩 Filtre onglet", ["Tous", "tab1", "tab2"], index=0)

st.sidebar.markdown("---")

# Mapping exercice (valeurs loggées côté élèves)
exercice_map = {
    "Exercice 1": ["Ex.1", "Exercice 1", "Exercice_1"],
    "Exercice 2": ["Ex.2", "Exercice 2", "Exercice_2"],
    "Exercice 3": ["Ex.3", "Exercice 3", "Exercice_3"],
}

# Tabs pour affichage
tab1, tab2, tab3 = st.tabs(["Ex.1", "Ex.2", "Ex.3"])


def list_all_objects(bucket: str):
    """Liste tous les objets du bucket (pagination)."""
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            yield obj["Key"]


def safe_json_loads(s: str):
    try:
        return json.loads(s)
    except Exception:
        return None


def normalize_exercice(value: str) -> str:
    if not value:
        return ""
    return value.strip()


def get_logs(date: str):
    """Charge tous les logs du jour (filtrés par champ 'jour')."""
    data = []
    for key in list_all_objects(BUCKET_NAME):
        if not key.endswith(".json"):
            continue
        obj_data = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        content = obj_data["Body"].read().decode("utf-8")
        parsed = safe_json_loads(content)
        if not isinstance(parsed, dict):
            continue
        if parsed.get("jour") == date:
            parsed["_s3_key"] = key  # utile si debug
            data.append(parsed)
    return data


def filter_logs_for_exercice(logs, exercice_variants_list, tab_choice):
    out = []
    for r in logs:
        ex = normalize_exercice(r.get("exercice", ""))
        if ex not in exercice_variants_list:
            continue
        if tab_choice != "Tous" and r.get("tab") != tab_choice:
            continue
        out.append(r)
    return out


def afficher_resultats(tab, exercice_title, exercice_variants_list):
    with tab:
        st.subheader(exercice_title)

        if st.button("📊 Visualiser les réponses", key=f"btn_{exercice_title}"):
            logs_all = get_logs(date_filter)
            logs = filter_logs_for_exercice(logs_all, exercice_variants_list, tab_filter)

            if not logs:
                st.info("Aucune donnée trouvée pour les filtres sélectionnés.")
                return

            df = pd.DataFrame(logs)

            # Harmonise "response" / "reponse"
            if "reponse" in df.columns and "response" not in df.columns:
                df["response"] = df["reponse"]

            # Assure les colonnes minimales
            if "prompt" not in df.columns:
                df["prompt"] = ""
            if "response" not in df.columns:
                df["response"] = ""

            # Tableau synthèse
            df_display = df.drop(columns=["timestamp", "jour", "session_id", "_s3_key"], errors="ignore")
            st.data_editor(df_display, use_container_width=True, num_rows="dynamic")

            st.markdown("---")
            st.markdown("## 📄 Prompts et réponses détaillées")

            detail_df = df[["prompt", "response"]].copy()
            detail_df.columns = ["📝 Prompt", "💬 Réponse"]

            detail_rows = ""
            for _, row in detail_df.iterrows():
                prompt_html = f"<td style='vertical-align:top; white-space:pre-wrap;'>{row['📝 Prompt']}</td>"
                response_html = f"<td style='vertical-align:top; white-space:pre-wrap;'>{row['💬 Réponse']}</td>"
                detail_rows += f"<tr>{prompt_html}{response_html}</tr>"

            st.markdown(f"""
            <table style='width:100%; border-collapse: collapse;'>
              <thead>
                <tr>
                  <th style='text-align:left; border-bottom: 2px solid #ccc;'>📝 Prompt</th>
                  <th style='text-align:left; border-bottom: 2px solid #ccc;'>💬 Réponse</th>
                </tr>
              </thead>
              <tbody>
                {detail_rows}
              </tbody>
            </table>
            """, unsafe_allow_html=True)


# Affichage dans les tabs Ex.1/Ex.2/Ex.3
afficher_resultats(tab1, "Ex.1 Générer un support de communication", exercice_map["Exercice 1"])
afficher_resultats(tab2, "Ex.2 Contruire un plan de formation", exercice_map["Exercice 2"])
afficher_resultats(tab3, "Ex.3 Extraction des informations dans un narratif", exercice_map["Exercice 3"])
