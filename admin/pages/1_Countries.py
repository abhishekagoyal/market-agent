import streamlit as st
import os, sys, pytz

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

st.set_page_config(page_title="Countries", page_icon="🌍", layout="wide")
st.title("Countries")
st.caption("Add and manage countries. Each country has its own timezone, categories and schedule.")

config    = load_config()
countries = config.get("countries", {})

for key, cfg in list(countries.items()):
    with st.expander(f"{cfg.get('flag','')} {cfg.get('label', key)} — {len(cfg.get('categories',{}))} categories"):
        col1, col2, col3 = st.columns([2,2,1])
        label    = col1.text_input("Label",    value=cfg.get("label", key),    key=f"label_{key}")
        flag     = col2.text_input("Flag emoji", value=cfg.get("flag", "🌐"),  key=f"flag_{key}")
        timezone = col3.selectbox("Timezone",
            options=pytz.all_timezones,
            index=pytz.all_timezones.index(cfg.get("timezone","UTC")) if cfg.get("timezone","UTC") in pytz.all_timezones else 0,
            key=f"tz_{key}"
        )
        c1, c2 = st.columns([1,5])
        if c1.button("Save", key=f"save_{key}"):
            config["countries"][key]["label"]    = label
            config["countries"][key]["flag"]     = flag
            config["countries"][key]["timezone"] = timezone
            save_config(config)
            st.success("Saved!")
            st.rerun()
        if c2.button("Delete country", key=f"del_{key}", type="secondary"):
            del config["countries"][key]
            save_config(config)
            st.success(f"Deleted {label}")
            st.rerun()

st.divider()
st.subheader("Add new country")
col1, col2, col3 = st.columns([2,1,2])
new_key  = col1.text_input("Country code (e.g. UK, IN, SG)")
new_flag = col2.text_input("Flag emoji", value="🌐")
new_tz   = col3.selectbox("Timezone", options=pytz.all_timezones,
    index=pytz.all_timezones.index("UTC"))
new_label = st.text_input("Display name (e.g. United Kingdom)")

if st.button("Add country", type="primary"):
    if new_key and new_label:
        if new_key in config["countries"]:
            st.error("Country code already exists!")
        else:
            config["countries"][new_key] = {
                "label": new_label,
                "flag": new_flag,
                "timezone": new_tz,
                "categories": {}
            }
            save_config(config)
            st.success(f"Added {new_label}!")
            st.rerun()
    else:
        st.error("Please fill in country code and display name.")