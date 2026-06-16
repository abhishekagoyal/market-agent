import streamlit as st
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("S3_BUCKET_NAME", "market-agent-abhis")

try:
    os.environ["AWS_ACCESS_KEY_ID"]     = st.secrets["AWS_ACCESS_KEY_ID"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets["AWS_SECRET_ACCESS_KEY"]
    os.environ["AWS_DEFAULT_REGION"]    = st.secrets.get("AWS_DEFAULT_REGION", "us-east-1")
except Exception:
    pass

from dotenv import load_dotenv
load_dotenv()
from config.config_manager import load_config

st.set_page_config(page_title="Agent Admin", page_icon="⚙️", layout="wide")
st.title("Market Agent — Admin")
st.caption("Configure countries, categories, news sources, Telegram recipients and schedules")

config   = load_config()
countries = config.get("countries", {})

total_cats       = sum(len(c.get("categories", {})) for c in countries.values())
total_feeds      = sum(
    len(cat.get("feeds", {}))
    for c in countries.values()
    for cat in c.get("categories", {}).values()
)
total_recipients = sum(
    len(cat.get("telegram_recipients", []))
    for c in countries.values()
    for cat in c.get("categories", {}).values()
)
total_scheduled  = sum(
    1 for c in countries.values()
    for cat in c.get("categories", {}).values()
    if cat.get("enabled") and cat.get("schedule")
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Countries",        len(countries))
c2.metric("Categories",       total_cats)
c3.metric("News sources",     total_feeds)
c4.metric("Telegram recipients", total_recipients)

st.divider()
st.subheader("Schedule overview")

rows = []
for country_key, country_cfg in countries.items():
    for cat_key, cat_cfg in country_cfg.get("categories", {}).items():
        sched = cat_cfg.get("schedule", {})
        rows.append({
            "Country":  f"{country_cfg.get('flag','')} {country_cfg.get('label', country_key)}",
            "Category": cat_cfg.get("label", cat_key),
            "Time":     f"{sched.get('hour',0):02d}:{sched.get('minute',0):02d} {country_cfg.get('timezone','')}",
            "Status":   "✅ Active" if cat_cfg.get("enabled") else "⏸ Paused",
            "Recipients": len(cat_cfg.get("telegram_recipients", []))
        })

if rows:
    import pandas as pd
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.info("No categories configured yet. Use the sidebar to add countries and categories.")