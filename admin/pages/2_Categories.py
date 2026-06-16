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

st.set_page_config(page_title="Categories", page_icon="📂", layout="wide")
st.title("Categories")

config    = load_config()
countries = config.get("countries", {})

if not countries:
    st.warning("No countries configured yet. Add a country first.")
    st.stop()

country_options = {f"{v.get('flag','')} {v.get('label',k)}": k for k, v in countries.items()}
selected_label  = st.selectbox("Country", list(country_options.keys()))
country_key     = country_options[selected_label]
country_cfg     = countries[country_key]
categories      = country_cfg.get("categories", {})

st.caption(f"{len(categories)} categories in {country_cfg.get('label', country_key)}")
st.divider()

for cat_key, cat_cfg in list(categories.items()):
    status = "✅" if cat_cfg.get("enabled") else "⏸"
    with st.expander(f"{status} {cat_cfg.get('label', cat_key)}"):
        col1, col2 = st.columns(2)
        label       = col1.text_input("Label",       value=cat_cfg.get("label", cat_key),         key=f"label_{cat_key}")
        prompt_role = col2.text_input("Analyst role", value=cat_cfg.get("prompt_role", "analyst"), key=f"role_{cat_key}")
        prompt_focus = st.text_area("Briefing focus", value=cat_cfg.get("prompt_focus", ""),       key=f"focus_{cat_key}", height=80)
        enabled = st.toggle("Enabled", value=cat_cfg.get("enabled", True), key=f"enabled_{cat_key}")

        c1, c2, _ = st.columns([1, 1, 4])
        if c1.button("Save", key=f"save_{cat_key}"):
            config["countries"][country_key]["categories"][cat_key].update({
                "label": label, "prompt_role": prompt_role,
                "prompt_focus": prompt_focus, "enabled": enabled
            })
            save_config(config)
            st.success("Saved!")
            st.rerun()
        if c2.button("Delete", key=f"del_{cat_key}", type="secondary"):
            del config["countries"][country_key]["categories"][cat_key]
            save_config(config)
            st.success(f"Deleted {label}")
            st.rerun()

st.divider()
st.subheader("Add new category")
col1, col2 = st.columns(2)
new_key   = col1.text_input("Category key (e.g. crypto, sports)")
new_label = col2.text_input("Display label (e.g. Crypto & Web3)")
new_role  = st.text_input("Analyst role", value="industry analyst")
new_focus = st.text_area("Briefing focus", value="key themes, risks, and opportunities", height=80)

if st.button("Add category", type="primary"):
    if new_key and new_label:
        config["countries"][country_key]["categories"][new_key] = {
            "label": new_label, "prompt_role": new_role,
            "prompt_focus": new_focus, "enabled": True,
            "feeds": {}, "schedule": {"hour": 9, "minute": 0},
            "telegram_recipients": []
        }
        save_config(config)
        st.success(f"Added {new_label}!")
        st.rerun()
    else:
        st.error("Please fill in category key and label.")