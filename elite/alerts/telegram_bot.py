"""
alerts/telegram_bot.py
Sends a message to your Telegram chat.
Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in config.py.
"""

import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_alert(message: str) -> bool:
    if "YOUR_BOT_TOKEN" in TELEGRAM_BOT_TOKEN:
        print(f"  [telegram] (not configured) {message}")
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
        return r.ok
    except Exception as e:
        print(f"  [telegram] error: {e}")
        return False
