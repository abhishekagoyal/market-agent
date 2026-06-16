import streamlit as st
import os, sys, json, boto3
from datetime import datetime
import pytz

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

LAMBDA_ARN = "arn:aws:lambda:us-east-1:713716300707:function:market-agent"

def get_clients():
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    key    = os.getenv("AWS_ACCESS_KEY_ID")
    secret = os.getenv("AWS_SECRET_ACCESS_KEY")
    kwargs = {"region_name": region}
    if key and secret:
        kwargs["aws_access_key_id"]     = key
        kwargs["aws_secret_access_key"] = secret
    return boto3.client("events", **kwargs), boto3.client("lambda", **kwargs)

def local_to_utc(hour, minute, timezone_str):
    tz      = pytz.timezone(timezone_str)
    local   = tz.localize(datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0))
    utc     = local.astimezone(pytz.utc)
    return utc.hour, utc.minute

def update_rule(country, cat_key, hour, minute, timezone_str, enabled):
    events, lmb = get_clients()
    rule_name   = f"market-agent-{country.lower()}-{cat_key.lower()}"
    utc_h, utc_m = local_to_utc(hour, minute, timezone_str)
    state = "ENABLED" if enabled else "DISABLED"
    events.put_rule(
        Name=rule_name,
        ScheduleExpression=f"cron({utc_m} {utc_h} * * ? *)",
        State=state
    )
    try:
        lmb.add_permission(
            FunctionName="market-agent",
            StatementId=f"eventbridge-{country.lower()}-{cat_key.lower()}",
            Action="lambda:InvokeFunction",
            Principal="events.amazonaws.com"
        )
    except Exception:
        pass
    try:
        events.put_targets(
            Rule=rule_name,
            Targets=[{
                "Id": f"target-{country}-{cat_key}",
                "Arn": LAMBDA_ARN,
                "Input": json.dumps({"country": country, "category": cat_key})
            }]
        )
    except Exception as e:
        st.error(f"Target error: {e}")
    return utc_h, utc_m

st.set_page_config(page_title="Scheduler", page_icon="⏰", layout="wide")
st.title("Scheduler")
st.caption("Set run times per country and category. Changes update EventBridge automatically.")

config    = load_config()
countries = config.get("countries", {})

if not countries:
    st.warning("No countries configured yet.")
    st.stop()

for country_key, country_cfg in countries.items():
    st.subheader(f"{country_cfg.get('flag','')} {country_cfg.get('label', country_key)}")
    timezone_str = country_cfg.get("timezone", "UTC")
    categories   = country_cfg.get("categories", {})

    for cat_key, cat_cfg in categories.items():
        sched   = cat_cfg.get("schedule", {"hour": 8, "minute": 0})
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        col1.markdown(f"**{cat_cfg.get('label', cat_key)}**")
        col1.caption(timezone_str)

        time_val = datetime.now().replace(
            hour=sched.get("hour", 8),
            minute=sched.get("minute", 0)
        ).strftime("%H:%M")

        new_time = col2.text_input(
            "Time (HH:MM)", value=time_val,
            key=f"time_{country_key}_{cat_key}"
        )
        enabled = col3.toggle(
            "Enabled", value=cat_cfg.get("enabled", True),
            key=f"enabled_{country_key}_{cat_key}"
        )

        if col4.button("Save", key=f"save_{country_key}_{cat_key}", type="primary"):
            try:
                h, m = map(int, new_time.split(":"))
                utc_h, utc_m = update_rule(country_key, cat_key, h, m, timezone_str, enabled)
                config["countries"][country_key]["categories"][cat_key].update({
                    "schedule": {"hour": h, "minute": m},
                    "enabled": enabled
                })
                save_config(config)
                st.success(f"Updated! Runs at {new_time} {timezone_str} ({utc_h:02d}:{utc_m:02d} UTC)")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()