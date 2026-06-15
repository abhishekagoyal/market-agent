import os, asyncio
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN    = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_IDS = os.getenv("TELEGRAM_CHAT_IDS", "")

async def _send(chat_id, text):
    from telegram import Bot
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=chat_id, text=text)

async def _send_all(text):
    chat_ids = [cid.strip() for cid in TELEGRAM_CHAT_IDS.split(",") if cid.strip()]
    for chat_id in chat_ids:
        await _send(chat_id, text)

def send_briefing(analysis, article_count, category="finance"):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_IDS:
        print("Telegram not configured — skipping.")
        return
    msg = (
        f"Daily Briefing\n"
        f"Category: {category}\n"
        f"{article_count} articles analyzed\n\n"
        f"{analysis}"
    )
    asyncio.run(_send_all(msg))
