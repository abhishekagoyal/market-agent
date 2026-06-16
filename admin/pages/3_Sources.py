import streamlit as st
import os, sys
import feedparser

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

st.set_page_config(page_title="News Sources", page_icon="📰", layout="wide")
st.title("News sources")

config    = load_config()
countries = config.get("countries", {})

if not countries:
    st.warning("No countries configured yet.")
    st.stop()

col1, col2 = st.columns(2)
country_options  = {f"{v.get('flag','')} {v.get('label',k)}": k for k, v in countries.items()}
selected_country = col1.selectbox("Country", list(country_options.keys()))
country_key      = country_options[selected_country]
categories       = countries[country_key].get("categories", {})

if not categories:
    st.warning("No categories in this country yet.")
    st.stop()

cat_options  = {v.get("label", k): k for k, v in categories.items()}
selected_cat = col2.selectbox("Category", list(cat_options.keys()))
cat_key      = cat_options[selected_cat]
feeds        = categories[cat_key].get("feeds", {})

st.caption(f"{len(feeds)} sources configured")
st.divider()

for name, url in list(feeds.items()):
    col1, col2, col3 = st.columns([2, 4, 1])
    col1.markdown(f"**{name}**")
    col2.caption(url)
    if col3.button("Remove", key=f"del_{name}"):
        del config["countries"][country_key]["categories"][cat_key]["feeds"][name]
        save_config(config)
        st.success(f"Removed {name}")
        st.rerun()

st.divider()
st.subheader("Add new source")
col1, col2 = st.columns([1, 2])
new_name = col1.text_input("Source name (e.g. Bloomberg)")
new_url  = col2.text_input("RSS feed URL")

col1, col2 = st.columns([1, 5])
if col1.button("Add source", type="primary"):
    if new_name and new_url:
        config["countries"][country_key]["categories"][cat_key]["feeds"][new_name] = new_url
        save_config(config)
        st.success(f"Added {new_name}!")
        st.rerun()
    else:
        st.error("Please fill in both name and URL.")

if col2.button("Test feed URL"):
    if new_url:
        with st.spinner("Testing..."):
            try:
                feed = feedparser.parse(new_url)
                if feed.entries:
                    st.success(f"Feed works! Found {len(feed.entries)} entries. Latest: {feed.entries[0].get('title','')}")
                else:
                    st.warning("Feed parsed but no entries found. Check the URL.")
            except Exception as e:
                st.error(f"Feed failed: {e}")
    else:
        st.error("Enter a URL first.")