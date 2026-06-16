import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_telegram_message(message: str) -> dict:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {
            "sent": False,
            "reason": "Telegram bot token or chat id is missing.",
        }

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": str(TELEGRAM_CHAT_ID).strip(),
        "text": message[:3000],
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(url, data=payload, timeout=(10, 90))
        response.raise_for_status()

        return {
            "sent": True,
            "response": response.json(),
        }

    except requests.exceptions.ConnectTimeout:
        return {"sent": False, "reason": "Telegram connection timeout."}

    except requests.exceptions.ReadTimeout:
        return {"sent": False, "reason": "Telegram read timeout."}

    except requests.exceptions.ConnectionError as e:
        return {"sent": False, "reason": f"Telegram connection error: {e}"}

    except requests.RequestException as e:
        return {
            "sent": False,
            "reason": str(e),
            "response_text": getattr(e.response, "text", None) if getattr(e, "response", None) else None,
        }
