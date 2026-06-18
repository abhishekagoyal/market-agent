import streamlit as st
import os, sys
import json
import pandas as pd
import boto3

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

st.set_page_config(page_title="Market Pulse", page_icon="📈", layout="wide")
st.title("📈 Market Pulse")
st.caption("Manage watchlist, recipients, and settings for the Market Pulse agent.")

config = load_config()
mp     = config.get("market_pulse", {})

tab1, tab2, tab3 = st.tabs(["📊 Watchlist", "👥 Recipients", "⚙️ Settings"])

# ─── TAB 1: WATCHLIST ───────────────────────────────────────────────
with tab1:
    st.subheader("Stock Watchlist")
    watchlist = mp.get("watchlist", [])

    # Display current watchlist
    if watchlist:
        df = pd.DataFrame(watchlist)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No stocks in watchlist yet.")

    st.divider()

    # Add individual stock
    st.subheader("Add Stock")
    col1, col2, col3 = st.columns(3)
    new_ticker  = col1.text_input("Ticker (e.g. NVDA)").upper().strip()
    new_name    = col2.text_input("Company name")
    new_sector  = col3.selectbox("Sector", [
        "Index", "Technology", "Financials", "Healthcare",
        "Energy", "Commodities", "Bonds", "Consumer", "Industrials", "Real Estate", "Other"
    ])

    if st.button("Add Stock", type="primary"):
        if new_ticker and new_name:
            # Check for duplicates
            existing = [w["ticker"] for w in watchlist]
            if new_ticker in existing:
                st.error(f"{new_ticker} already in watchlist.")
            else:
                watchlist.append({"ticker": new_ticker, "name": new_name, "sector": new_sector})
                config["market_pulse"]["watchlist"] = watchlist
                save_config(config)
                st.success(f"Added {new_ticker}!")
                st.rerun()
        else:
            st.error("Please fill in ticker and company name.")

    st.divider()

    # CSV Upload
    st.subheader("Bulk Upload via CSV")
    st.caption("CSV must have columns: ticker, name, sector")

    # Download template
    template_df = pd.DataFrame([
        {"ticker": "NVDA", "name": "NVIDIA",   "sector": "Technology"},
        {"ticker": "JPM",  "name": "JPMorgan", "sector": "Financials"},
    ])
    st.download_button(
        "Download CSV Template",
        template_df.to_csv(index=False),
        "watchlist_template.csv",
        "text/csv"
    )

    uploaded = st.file_uploader("Upload watchlist CSV", type="csv")
    if uploaded:
        try:
            df_upload = pd.read_csv(uploaded)
            df_upload.columns = df_upload.columns.str.lower().str.strip()

            # Validate columns
            required = {"ticker", "name", "sector"}
            if not required.issubset(df_upload.columns):
                st.error(f"CSV must have columns: ticker, name, sector. Found: {list(df_upload.columns)}")
            else:
                df_upload["ticker"] = df_upload["ticker"].str.upper().str.strip()
                new_stocks   = df_upload.to_dict("records")
                existing     = {w["ticker"] for w in watchlist}
                added        = []
                skipped      = []
                for stock in new_stocks:
                    if stock["ticker"] in existing:
                        skipped.append(stock["ticker"])
                    else:
                        watchlist.append(stock)
                        existing.add(stock["ticker"])
                        added.append(stock["ticker"])

                if added:
                    config["market_pulse"]["watchlist"] = watchlist
                    save_config(config)
                    st.success(f"Added {len(added)} stocks: {', '.join(added)}")
                if skipped:
                    st.warning(f"Skipped {len(skipped)} duplicates: {', '.join(skipped)}")
                st.rerun()
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

    st.divider()

    # Remove stocks
    if watchlist:
        st.subheader("Remove Stock")
        ticker_to_remove = st.selectbox(
            "Select stock to remove",
            [f"{w['ticker']} — {w['name']}" for w in watchlist]
        )
        if st.button("Remove", type="secondary"):
            ticker_key = ticker_to_remove.split(" — ")[0]
            config["market_pulse"]["watchlist"] = [
                w for w in watchlist if w["ticker"] != ticker_key
            ]
            save_config(config)
            st.success(f"Removed {ticker_key}")
            st.rerun()


# ─── TAB 2: RECIPIENTS ──────────────────────────────────────────────
with tab2:
    st.subheader("Telegram Recipients")
    recipients = mp.get("recipients", [])

    if recipients:
        for i, rec in enumerate(recipients):
            with st.expander(f"{rec.get('name', 'Unknown')} — {rec.get('chat_id', '')}"):
                col1, col2 = st.columns(2)
                col1.text(f"Chat ID: {rec.get('chat_id', '')}")
                send_audit = col2.toggle(
                    "Send audit trail",
                    value=rec.get("send_audit", False),
                    key=f"audit_{i}"
                )
                c1, c2 = st.columns([1, 5])
                if c1.button("Save", key=f"save_rec_{i}"):
                    config["market_pulse"]["recipients"][i]["send_audit"] = send_audit
                    save_config(config)
                    st.success("Saved!")
                    st.rerun()
                if c2.button("Remove", key=f"del_rec_{i}", type="secondary"):
                    config["market_pulse"]["recipients"].pop(i)
                    save_config(config)
                    st.success("Removed")
                    st.rerun()
    else:
        st.info("No recipients yet.")

    st.divider()
    st.subheader("Add Recipient")
    col1, col2, col3 = st.columns(3)
    new_name    = col1.text_input("Name")
    new_chat_id = col2.text_input("Telegram Chat ID")
    new_audit   = col3.toggle("Send audit trail", value=False)

    if st.button("Add Recipient", type="primary"):
        if new_name and new_chat_id:
            recipients.append({
                "name":       new_name,
                "chat_id":    new_chat_id,
                "send_audit": new_audit
            })
            config["market_pulse"]["recipients"] = recipients
            save_config(config)
            st.success(f"Added {new_name}!")
            st.rerun()
        else:
            st.error("Please fill in name and chat ID.")


# ─── TAB 3: SETTINGS ────────────────────────────────────────────────
with tab3:
    st.subheader("Market Pulse Settings")

    schedule = mp.get("schedule", {"hour": 9, "minute": 0, "timezone": "America/New_York"})
    enabled  = mp.get("enabled", True)

    col1, col2, col3 = st.columns(3)
    hour     = col1.number_input("Hour",     min_value=0, max_value=23, value=schedule.get("hour", 9))
    minute   = col2.number_input("Minute",   min_value=0, max_value=59, value=schedule.get("minute", 0))
    timezone = col3.selectbox("Timezone", ["America/New_York", "UTC", "Asia/Kolkata"],
                              index=["America/New_York", "UTC", "Asia/Kolkata"].index(
                                  schedule.get("timezone", "America/New_York")))
    enabled  = st.toggle("Agent Enabled", value=enabled)

    st.caption("Note: After saving settings, go to AWS Console or use the Scheduler page to update the EventBridge rule for market-pulse Lambda.")

    if st.button("Save Settings", type="primary"):
        config["market_pulse"]["schedule"] = {"hour": hour, "minute": minute, "timezone": timezone}
        config["market_pulse"]["enabled"]  = enabled
        save_config(config)
        st.success("Settings saved!")
        st.rerun()

    st.divider()
    st.subheader("FRED Indicators")
    st.caption("These macro indicators are pulled from the Federal Reserve (FRED) on every run.")
    fred_indicators = mp.get("fred_indicators", [])
    for indicator in fred_indicators:
        st.text(f"• {indicator}")