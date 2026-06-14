import boto3, os, json
from datetime import datetime

BUCKET = os.getenv("S3_BUCKET_NAME", "market-agent-abhis")
s3     = boto3.client("s3", region_name="us-east-1")

def save_run(status, category="finance", articles=0, analysis="", error=""):
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
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix="runs/")
    objects  = sorted(
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