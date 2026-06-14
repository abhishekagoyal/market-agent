import os, asyncio
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

async def _send(text):
    from telegram import Bot
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)

def send_briefing(analysis, article_count):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured — skipping notification.")
        return
    msg = (
        f"Daily Market Briefing\n"
        f"{article_count} articles analyzed\n\n"
        f"{analysis}"
    )
    asyncio.run(_send(msg))