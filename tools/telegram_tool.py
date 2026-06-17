import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(message:str)->dict:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID: return {"sent":False,"reason":"Telegram bot token or chat id is missing."}
    url=f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"; payload={"chat_id":str(TELEGRAM_CHAT_ID).strip(),"text":str(message)[:3000],"disable_web_page_preview":True}
    try:
        r=requests.post(url,data=payload,timeout=(10,90)); print("Telegram Status Code:",r.status_code); print("Telegram Response:",r.text); r.raise_for_status(); return {"sent":True,"response":r.json()}
    except requests.RequestException as e: return {"sent":False,"reason":str(e),"response_text":r.text if 'r' in locals() else None}
