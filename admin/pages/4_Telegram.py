import streamlit as st
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
os.environ.setdefault("S3_BUCKET_NAME", "market-agent-abhis")
try:
    os.environ["AWS_ACCESS_KEY_ID"]     = st.secrets["AWS_ACCESS_KEY_ID"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets["AWS_SECRET_ACCESS_KEY"]
    os.environ["AWS_DEFAULT_REGION"]    = st.secrets.get("AWS_DEFAULT_REGION", "us-east-1")
except Exception:
    pass

from dotenv import load_dotenv
load_dotenv()
from config.config_manager import load_config, save_config

st.set_page_config(page_title="Telegram", page_icon="✈️", layout="wide")
st.title("Telegram recipients")
st.caption("Add recipients per category. They must start your bot before receiving messages.")

config    = load_config()
countries = config.get("countries", {})

if not countries:
    st.warning("No countries configured yet.")
    st.stop()

country_options  = {f"{v.get('flag','')} {v.get('label',k)}": k for k, v in countries.items()}
selected_country = st.selectbox("Country", list(country_options.keys()))
country_key      = country_options[selected_country]
categories       = countries[country_key].get("categories", {})

if not categories:
    st.warning("No categories in this country yet.")
    st.stop()

for cat_key, cat_cfg in categories.items():
    recipients = cat_cfg.get("telegram_recipients", [])
    st.subheader(f"{cat_cfg.get('label', cat_key)}")

    if recipients:
        for i, r in enumerate(recipients):
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            new_name = col1.text_input("Name", value=r.get("name",""), key=f"name_{cat_key}_{i}")
            new_id   = col2.text_input("Chat ID", value=r.get("id",""), key=f"id_{cat_key}_{i}")
            if col3.button("Save", key=f"save_{cat_key}_{i}"):
                config["countries"][country_key]["categories"][cat_key]["telegram_recipients"][i] = {
                    "name": new_name, "id": new_id
                }
                save_config(config)
                st.success("Saved!")
                st.rerun()
            if col4.button("Remove", key=f"del_{cat_key}_{i}"):
                config["countries"][country_key]["categories"][cat_key]["telegram_recipients"].pop(i)
                save_config(config)
                st.success("Removed!")
                st.rerun()
    else:
        st.caption("No recipients yet for this category.")

    with st.expander(f"Add recipient to {cat_cfg.get('label', cat_key)}"):
        col1, col2 = st.columns(2)
        add_name = col1.text_input("Name", key=f"addname_{cat_key}")
        add_id   = col2.text_input("Telegram Chat ID", key=f"addid_{cat_key}")
        st.caption("To get chat ID: open Telegram → search @userinfobot → send any message")
        if st.button("Add recipient", key=f"addbtn_{cat_key}", type="primary"):
            if add_name and add_id:
                config["countries"][country_key]["categories"][cat_key]["telegram_recipients"].append({
                    "name": add_name, "id": add_id
                })
                save_config(config)
                st.success(f"Added {add_name}!")
                st.rerun()
            else:
                st.error("Please fill in both name and chat ID.")
    st.divider()