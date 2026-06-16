import os, asyncio, sys
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")

async def _send(chat_id, text):
    from telegram import Bot
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=chat_id, text=text)

async def _send_all(recipients, text):
    for r in recipients:
        try:
            await _send(r["id"], text)
        except Exception as e:
            print(f"Failed to send to {r.get('name', r['id'])}: {e}")

def send_briefing(analysis, article_count, country="US", category="finance"):
    if not TELEGRAM_TOKEN:
        print("Telegram token not configured — skipping.")
        return

    from config.config_manager import load_config, get_recipients_for_category
    config     = load_config()
    recipients = get_recipients_for_category(config, country, category)

    global_ids = os.getenv("TELEGRAM_CHAT_IDS", "")
    if global_ids:
        for gid in global_ids.split(","):
            gid = gid.strip()
            if gid and not any(r["id"] == gid for r in recipients):
                recipients.append({"name": "global", "id": gid})

    if not recipients:
        print("No Telegram recipients configured — skipping.")
        return

    cat_cfg   = config["countries"].get(country, {}).get("categories", {}).get(category, {})
    cat_label = cat_cfg.get("label", category)
    msg = (
        f"Daily Briefing\n"
        f"{country} · {cat_label}\n"
        f"{article_count} articles analyzed\n\n"
        f"{analysis}"
    )
    asyncio.run(_send_all(recipients, msg))