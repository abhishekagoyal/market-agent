import os, sys, logging
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fetcher    import fetch_news
from analyzer   import analyze_news
from storage_s3 import save_run
from notifier   import send_briefing

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)

def run_agent(country="US", category="finance"):
    from config.config_manager import load_config
    config    = load_config()
    cat_cfg   = config["countries"].get(country, {}).get("categories", {}).get(category, {})
    label     = cat_cfg.get("label", category)
    log.info(f"--- Agent run started: {country} / {label} ---")
    try:
        articles = fetch_news(country, category)
        analysis = analyze_news(articles, country, category)
        save_run("success", category, len(articles), analysis)
        send_briefing(analysis, len(articles), country, category)
        log.info(f"Done - {len(articles)} articles processed")
        print(f"\n[{country} / {label}]\n" + analysis + "\n")
    except Exception as e:
        log.error(f"Run failed: {e}")
        save_run("error", category, error=str(e))

def handler(event, context):
    country  = event.get("country", "US")
    category = event.get("category", "finance")
    run_agent(country, category)
    return {"statusCode": 200, "body": f"Done - {country}/{category}"}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once",     action="store_true")
    parser.add_argument("--country",  default="US")
    parser.add_argument("--category", default="finance")
    args = parser.parse_args()

    if args.once:
        run_agent(args.country, args.category)
    else:
        run_agent(args.country, args.category)
        from apscheduler.schedulers.blocking import BlockingScheduler
        from config.config_manager import load_config
        config    = load_config()
        scheduler = BlockingScheduler(timezone="America/New_York")
        for country, country_cfg in config["countries"].items():
            for cat_key, cat_cfg in country_cfg.get("categories", {}).items():
                if cat_cfg.get("enabled") and cat_cfg.get("schedule"):
                    sched = cat_cfg["schedule"]
                    scheduler.add_job(
                        run_agent, "cron",
                        kwargs={"country": country, "category": cat_key},
                        hour=sched["hour"],
                        minute=sched["minute"]
                    )
                    log.info(f"Scheduled {country}/{cat_cfg['label']} at {sched['hour']:02d}:{sched['minute']:02d}")
        log.info("Scheduler active. Ctrl+C to stop.")
        try:
            scheduler.start()
        except KeyboardInterrupt:
            log.info("Stopped.")