import requests
from config import TELEGRAM_BOT_TOKEN

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"

try:
    response = requests.get(url, timeout=(10, 60))
    print("Status Code:", response.status_code)
    print("Response:", response.text)

except Exception as e:
    print("Error:", e)
    