import os
import requests

def send_telegram_message(message: str, chat_id: str, bot_token: str) -> bool:
    """Send a message via Telegram bot."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id":    chat_id,
        "text":       message,
        "parse_mode": "Markdown"
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"Telegram error: {e}")
        return False


def send_market_pulse(analysis: dict, formatted_message: str, 
                      audit_message: str, recipients: list, 
                      bot_token: str) -> dict:
    """
    Send Market Pulse briefing to all recipients.
    Each recipient is a dict: {"chat_id": "123", "send_audit": True/False}
    """
    results = {"sent": [], "failed": [], "audit_sent": []}

    for recipient in recipients:
        chat_id    = str(recipient.get("chat_id", ""))
        send_audit = recipient.get("send_audit", False)

        if not chat_id:
            continue

        # Send main pulse message
        ok = send_telegram_message(formatted_message, chat_id, bot_token)
        if ok:
            results["sent"].append(chat_id)
        else:
            results["failed"].append(chat_id)

        # Send audit trail if recipient wants it
        if ok and send_audit:
            send_telegram_message(audit_message, chat_id, bot_token)
            results["audit_sent"].append(chat_id)

    return results