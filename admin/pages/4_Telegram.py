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
st.caption("Add recipients once and choose which categories they receive.")

config    = load_config()
countries = config.get("countries", {})

if not countries:
    st.warning("No countries configured yet.")
    st.stop()

country_options  = {f"{v.get('flag','')} {v.get('label',k)}": k for k, v in countries.items()}
selected_country = st.selectbox("Country", list(country_options.keys()))
country_key      = country_options[selected_country]
country_cfg      = countries[country_key]
categories       = country_cfg.get("categories", {})
category_labels  = {k: v.get("label", k) for k, v in categories.items()}

if "telegram_recipients" not in config["countries"][country_key]:
    config["countries"][country_key]["telegram_recipients"] = []
    save_config(config)

recipients = config["countries"][country_key].get("telegram_recipients", [])

st.divider()

if recipients:
    st.subheader(f"Recipients ({len(recipients)})")
    for i, r in enumerate(recipients):
        with st.expander(f"{r.get('name','Unknown')} — {r.get('id','')}"):
            col1, col2 = st.columns(2)
            name    = col1.text_input("Name",      value=r.get("name",""),  key=f"name_{i}")
            chat_id = col2.text_input("Chat ID",   value=r.get("id",""),    key=f"id_{i}")

            receive_all = st.checkbox(
                "Receive all categories",
                value=r.get("receive_all", True),
                key=f"all_{i}"
            )

            selected_cats = []
            if not receive_all:
                selected_cats = st.multiselect(
                    "Select categories",
                    options=list(categories.keys()),
                    default=[c for c in r.get("categories", []) if c in categories],
                    format_func=lambda x: category_labels.get(x, x),
                    key=f"cats_{i}"
                )

            c1, c2 = st.columns([1, 5])
            if c1.button("Save", key=f"save_{i}"):
                config["countries"][country_key]["telegram_recipients"][i] = {
                    "name": name, "id": chat_id,
                    "receive_all": receive_all,
                    "categories": selected_cats
                }
                save_config(config)
                st.success("Saved!")
                st.rerun()
            if c2.button("Remove", key=f"del_{i}"):
                config["countries"][country_key]["telegram_recipients"].pop(i)
                save_config(config)
                st.success("Removed!")
                st.rerun()
else:
    st.info("No recipients yet. Add one below.")

st.divider()
st.subheader("Add recipient")
col1, col2 = st.columns(2)
new_name = col1.text_input("Name")
new_id   = col2.text_input("Telegram Chat ID")
st.caption("To get chat ID: open Telegram → search @userinfobot → send any message")

new_all  = st.checkbox("Receive all categories", value=True, key="new_all")
new_cats = []
if not new_all:
    new_cats = st.multiselect(
        "Select categories",
        options=list(categories.keys()),
        format_func=lambda x: category_labels.get(x, x),
        key="new_cats"
    )

if st.button("Add recipient", type="primary"):
    if new_name and new_id:
        config["countries"][country_key]["telegram_recipients"].append({
            "name": new_name, "id": new_id,
            "receive_all": new_all,
            "categories": new_cats
        })
        save_config(config)
        st.success(f"Added {new_name}!")
        st.rerun()
    else:
        st.error("Please fill in both name and chat ID.")