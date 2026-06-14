import os, sys, logging
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))
from fetcher    import fetch_news
from analyzer   import analyze_news
from storage_s3 import save_run
from notifier   import send_briefing
from categories import CATEGORIES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)

def run_agent(category="finance"):
    label = CATEGORIES.get(category, {}).get("label", category)
    log.info(f"--- Agent run started: {label} ---")
    try:
        articles = fetch_news(category)
        analysis = analyze_news(articles, category)
        save_run("success", category, len(articles), analysis)
        send_briefing(analysis, len(articles))
        log.info(f"Done - {len(articles)} articles processed")
        print(f"\n[{label}]\n" + analysis + "\n")
    except Exception as e:
        log.error(f"Run failed: {e}")
        save_run("error", category, error=str(e))

def handler(event, context):
    """AWS Lambda entry point"""
    category = event.get("category", "finance")
    run_agent(category)
    return {"statusCode": 200, "body": f"Done - {category}"}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once",     action="store_true")
    parser.add_argument("--category", default=None)
    args = parser.parse_args()

    if args.once:
        run_agent(args.category or "finance")
    else:
        run_agent(args.category or "finance")
        from apscheduler.schedulers.blocking import BlockingScheduler
        scheduler = BlockingScheduler(timezone="America/New_York")
        for cat, config in CATEGORIES.items():
            if args.category and cat != args.category:
                continue
            if config.get("schedule"):
                scheduler.add_job(
                    run_agent, "cron",
                    kwargs={"category": cat},
                    hour=config["schedule"]["hour"],
                    minute=config["schedule"]["minute"]
                )
                log.info(f"Scheduled {config['label']} daily at {config['schedule']['hour']:02d}:00")
        log.info("Scheduler active. Ctrl+C to stop.")
        try:
            scheduler.start()
        except KeyboardInterrupt:
            log.info("Stopped.")