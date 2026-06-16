import boto3, json, os

BUCKET = os.getenv("S3_BUCKET_NAME", "market-agent-abhis")
CONFIG_KEY = "config/agent_config.json"

def _get_s3():
    try:
        import streamlit as st
        return boto3.client(
            "s3",
            region_name=st.secrets.get("AWS_DEFAULT_REGION", "us-east-1"),
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"]
        )
    except Exception:
        return boto3.client("s3", region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1"))

def load_config():
    s3 = _get_s3()
    try:
        response = s3.get_object(Bucket=BUCKET, Key=CONFIG_KEY)
        return json.loads(response["Body"].read())
    except s3.exceptions.NoSuchKey:
        return default_config()
    except Exception as e:
        print(f"Config load error: {e}")
        return default_config()

def save_config(config):
    s3 = _get_s3()
    s3.put_object(
        Bucket=BUCKET,
        Key=CONFIG_KEY,
        Body=json.dumps(config, indent=2),
        ContentType="application/json"
    )

def default_config():
    return {
        "countries": {
            "US": {
                "label": "United States",
                "flag": "🇺🇸",
                "timezone": "America/New_York",
                "telegram_recipients": [],
                "categories": {
                    "finance": {
                        "label": "Finance & Markets",
                        "feeds": {
                            "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
                            "MarketWatch": "https://feeds.marketwatch.com/marketwatch/topstories/",
                            "CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html"
                        },
                        "prompt_role": "capital markets analyst",
                        "prompt_focus": "macro/market themes, key risks, and a sector in focus",
                        "enabled": True,
                        "schedule": {"hour": 8, "minute": 30},
                        "telegram_recipients": []
                    },
                    "tech": {
                        "label": "Technology",
                        "feeds": {
                            "TechCrunch": "https://techcrunch.com/feed/",
                            "The Verge": "https://www.theverge.com/rss/index.xml",
                            "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index"
                        },
                        "prompt_role": "technology industry analyst",
                        "prompt_focus": "key product launches, industry trends, and companies to watch",
                        "enabled": True,
                        "schedule": {"hour": 10, "minute": 0},
                        "telegram_recipients": []
                    },
                    "real_estate": {
                        "label": "Real Estate",
                        "feeds": {
                            "HousingWire": "https://www.housingwire.com/feed/",
                            "Inman": "https://www.inman.com/feed/"
                        },
                        "prompt_role": "real estate market analyst",
                        "prompt_focus": "market trends, mortgage rates, and regional hotspots",
                        "enabled": True,
                        "schedule": {"hour": 11, "minute": 0},
                        "telegram_recipients": []
                    },
                    "fashion": {
                        "label": "Fashion & Retail",
                        "feeds": {
                            "WWD": "https://wwd.com/feed/",
                            "Fashionista": "https://fashionista.com/.rss/excerpt/"
                        },
                        "prompt_role": "fashion industry analyst",
                        "prompt_focus": "brand news, trend directions, and retail performance",
                        "enabled": True,
                        "schedule": {"hour": 11, "minute": 30},
                        "telegram_recipients": []
                    }
                }
            }
        }
    }
def get_recipients_for_category(config, country, category):
    country_cfg = config["countries"].get(country, {})
    all_recipients = country_cfg.get("telegram_recipients", [])
    return [
        r for r in all_recipients
        if r.get("receive_all", True) or category in r.get("categories", [])
    ]