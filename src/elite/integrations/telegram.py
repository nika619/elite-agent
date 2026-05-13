"""
elite.integrations.telegram
Telegram Bot API integration for push notifications.
Silently no-ops when credentials are not configured.
"""

from __future__ import annotations

import logging

import requests

from elite.config.settings import get_settings

logger = logging.getLogger(__name__)


def send_alert(message: str) -> bool:
    """
    Send a message to the configured Telegram chat.

    Returns True on success, False if unconfigured or on failure.
    No exceptions are raised — this is a fire-and-forget notification.
    """
    settings = get_settings()

    if not settings.telegram_configured:
        logger.debug("Telegram not configured, skipping alert: %s", message[:80])
        return False

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"

    try:
        response = requests.post(
            url,
            json={"chat_id": settings.telegram_chat_id, "text": message},
            timeout=10,
        )
        if response.ok:
            logger.info("Telegram alert sent successfully")
            return True
        else:
            logger.warning(
                "Telegram API returned %d: %s",
                response.status_code,
                response.text[:200],
            )
            return False
    except requests.exceptions.Timeout:
        logger.warning("Telegram request timed out")
        return False
    except Exception as e:
        logger.error("Telegram send failed: %s", e)
        return False
