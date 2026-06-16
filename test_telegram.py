import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

payload = {
    "chat_id": TELEGRAM_CHAT_ID,
    "text": "Telegram test message from crypto research agent"
}

response = requests.post(url, json=payload, timeout=30)

print("Status Code:", response.status_code)
print("Response:", response.text)
