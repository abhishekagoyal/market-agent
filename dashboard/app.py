import streamlit as st
import os, sys

# Load AWS credentials from Streamlit secrets
if hasattr(st, "secrets"):
    os.environ["AWS_ACCESS_KEY_ID"]     = st.secrets.get("AWS_ACCESS_KEY_ID", "")
    os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets.get("AWS_SECRET_ACCESS_KEY", "")
    os.environ["AWS_DEFAULT_REGION"]    = st.secrets.get("AWS_DEFAULT_REGION", "us-east-1")
    os.environ["S3_BUCKET_NAME"]        = st.secrets.get("S3_BUCKET_NAME", "market-agent-abhis")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agent"))
os.environ.setdefault("DB_PATH", "data/agent.db")
from dotenv import load_dotenv
load_dotenv()
from storage_s3 import get_runs
from categories import CATEGORIES

st.set_page_config(page_title="Intelligence Agent", layout="wide")
st.title("Intelligence Agent Dashboard")

# Category filter
cat_options = ["All"] + [CATEGORIES[c]["label"] for c in CATEGORIES]
cat_keys    = {CATEGORIES[c]["label"]: c for c in CATEGORIES}

selected_label = st.selectbox("Filter by category", cat_options)
selected_cat   = cat_keys.get(selected_label) if selected_label != "All" else None

runs    = get_runs(50, category=selected_cat)
total   = len(runs)
success = sum(1 for r in runs if r["status"] == "success")
rate    = f"{int(success / total * 100)}%" if total else "n/a"

c1, c2, c3 = st.columns(3)
c1.metric("Total runs",   total)
c2.metric("Successful",   success)
c3.metric("Success rate", rate)

st.divider()

latest = next((r for r in runs if r["status"] == "success"), None)
if latest:
    st.subheader("Latest briefing")
    ts        = latest["timestamp"][:16].replace("T", " ")
    cat_label = CATEGORIES.get(latest["category"], {}).get("label", "")
    st.caption(f"{ts}  ·  {latest['articles']} articles  ·  {cat_label}")
    st.info(latest["analysis"])
else:
    st.info("No runs yet.")

st.subheader("Run history")
for r in runs[:20]:
    ts        = r["timestamp"][:16].replace("T", " ")
    cat_label = CATEGORIES.get(r.get("category",""), {}).get("label", "")
    label     = f"{ts}  —  {cat_label}  —  {r['articles']} articles  [{r['status']}]"
    with st.expander(label):
        if r["analysis"]:
            st.write(r["analysis"])
        if r["error"]:
            st.error(r["error"])
