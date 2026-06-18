import os
import sys
import json

# Path setup for Lambda
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "market_pulse"))

from market_pulse.data_fetcher import get_market_pulse_data
from market_pulse.analyser import analyse
from market_pulse.formatter import format_telegram_message, format_audit_message
from market_pulse.notifier import send_market_pulse
from config.config_manager import load_config
import boto3
from datetime import datetime

def save_to_s3(data: dict, bucket: str) -> bool:
    """Save Market Pulse run results to S3 for audit and dashboard."""
    try:
        key    = os.environ.get("AWS_ACCESS_KEY_ID")
        secret = os.environ.get("AWS_SECRET_ACCESS_KEY")
        region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        kwargs = {"region_name": region}
        if key and secret:
            kwargs["aws_access_key_id"]     = key
            kwargs["aws_secret_access_key"] = secret
        s3     = boto3.client("s3", **kwargs)
        date   = datetime.utcnow().strftime("%Y/%m/%d")
        s3_key = f"market_pulse/{date}/run_{datetime.utcnow().strftime('%H%M%S')}.json"
        s3.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=json.dumps(data, indent=2),
            ContentType="application/json"
        )
        print(f"Saved to S3: {s3_key}")
        return True
    except Exception as e:
        print(f"S3 save error: {e}")
        return False


def handler(event, context):
    """Lambda entry point for Market Pulse agent."""
    print(f"Market Pulse triggered at {datetime.utcnow().isoformat()}")
    print(f"Event: {json.dumps(event)}")

    # Load config from S3
    config      = load_config()
    bucket      = os.environ.get("S3_BUCKET_NAME", "market-agent-abhis")
    bot_token   = os.environ.get("MARKET_PULSE_BOT_TOKEN", "")

    # Get watchlist from config
    watchlist   = config.get("market_pulse", {}).get("watchlist", [])
    tickers     = [item["ticker"] for item in watchlist if item.get("ticker")]
    recipients  = config.get("market_pulse", {}).get("recipients", [])

    if not tickers:
        print("No tickers in watchlist — exiting")
        return {"statusCode": 200, "body": "No tickers configured"}

    if not bot_token:
        print("No MARKET_PULSE_BOT_TOKEN set — exiting")
        return {"statusCode": 200, "body": "No bot token configured"}

    # 1. Fetch data
    print(f"Fetching data for {len(tickers)} tickers...")
    market_data = get_market_pulse_data(tickers)

    # 2. Pull recent news headlines from S3 (reuse market-agent's output)
    news_headlines = []
    try:
        key    = os.environ.get("AWS_ACCESS_KEY_ID")
        secret = os.environ.get("AWS_SECRET_ACCESS_KEY")
        region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        kwargs = {"region_name": region}
        if key and secret:
            kwargs["aws_access_key_id"]     = key
            kwargs["aws_secret_access_key"] = secret
        s3     = boto3.client("s3", **kwargs)
        date   = datetime.utcnow().strftime("%Y/%m/%d")
        # List recent market-agent runs from today
        resp   = s3.list_objects_v2(Bucket=bucket, Prefix=f"runs/{date}/")
        for obj in resp.get("Contents", [])[:5]:   # last 5 runs today
            body = s3.get_object(Bucket=bucket, Key=obj["Key"])
            run  = json.loads(body["Body"].read())
            for cat in run.get("categories", {}).values():
                for item in cat.get("items", [])[:3]:
                    headline = item.get("title", "")
                    if headline:
                        news_headlines.append(headline)
    except Exception as e:
        print(f"Could not load news from S3: {e} — continuing without headlines")

    # 3. Analyse
    print("Running Claude analysis...")
    analysis = analyse(
        macro=market_data["macro"],
        stocks=market_data["stocks"],
        news_headlines=news_headlines[:20]   # cap at 20 headlines
    )

    if "error" in analysis:
        print(f"Analysis error: {analysis['error']}")
        return {"statusCode": 500, "body": analysis["error"]}

    # 4. Format messages
    pulse_message = format_telegram_message(analysis, market_data["macro"])
    audit_message = format_audit_message(analysis)

    # 5. Send to recipients
    print(f"Sending to {len(recipients)} recipients...")
    send_results = send_market_pulse(
        analysis=analysis,
        formatted_message=pulse_message,
        audit_message=audit_message,
        recipients=recipients,
        bot_token=bot_token
    )
    print(f"Send results: {send_results}")

    # 6. Save full run to S3
    save_to_s3({
        "market_data": market_data,
        "analysis":    analysis,
        "send_results": send_results,
        "tickers":     tickers,
        "headlines_used": len(news_headlines)
    }, bucket)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message":      "Market Pulse sent",
            "sentiment":    analysis.get("overall_sentiment"),
            "tickers":      len(tickers),
            "recipients":   send_results.get("sent", []),
            "headlines":    len(news_headlines)
        })
    }