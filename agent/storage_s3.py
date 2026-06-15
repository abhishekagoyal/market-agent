import boto3, os, json
from datetime import datetime

BUCKET = "market-agent-abhis"

def _get_credentials():
    try:
        import streamlit as st
        return {
            "aws_access_key_id":     st.secrets["AWS_ACCESS_KEY_ID"],
            "aws_secret_access_key": st.secrets["AWS_SECRET_ACCESS_KEY"],
            "region_name":           st.secrets.get("AWS_DEFAULT_REGION", "us-east-1")
        }
    except Exception:
        return {
            "aws_access_key_id":     os.getenv("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "region_name":           os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        }

def _get_s3():
    return boto3.client("s3", **_get_credentials())

def save_run(status, category="finance", articles=0, analysis="", error=""):
    s3 = _get_s3()
    run = {
        "timestamp": datetime.now().isoformat(),
        "status":    status,
        "category":  category,
        "articles":  articles,
        "analysis":  analysis,
        "error":     error
    }
    key = f"runs/{run['timestamp']}-{category}.json"
    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=json.dumps(run),
        ContentType="application/json"
    )

def get_runs(limit=20, category=None):
    s3 = _get_s3()
    try:
        response = s3.list_objects_v2(Bucket=BUCKET, Prefix="runs/")
    except Exception as e:
        print(f"S3 error: {e}")
        return []
    objects = sorted(
        response.get("Contents", []),
        key=lambda x: x["Key"],
        reverse=True
    )
    runs = []
    for obj in objects:
        body = s3.get_object(Bucket=BUCKET, Key=obj["Key"])["Body"].read()
        run  = json.loads(body)
        if category and run.get("category") != category:
            continue
        runs.append(run)
        if len(runs) >= limit:
            break
    return runs
