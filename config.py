import os
from dotenv import load_dotenv
load_dotenv()
DEFAULT_SYMBOL=os.getenv("DEFAULT_SYMBOL","BTCUSDT")
REPORT_LANGUAGE=os.getenv("REPORT_LANGUAGE","ko")
BINANCE_SPOT_BASE_URL="https://api.binance.com"
BINANCE_FUTURES_BASE_URL="https://fapi.binance.com"
OLLAMA_BASE_URL=os.getenv("OLLAMA_BASE_URL","http://localhost:11434")
OLLAMA_MODEL=os.getenv("OLLAMA_MODEL","qwen2.5:3b")
SEND_TELEGRAM=os.getenv("SEND_TELEGRAM","false").lower()=="true"
TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN","")
TELEGRAM_CHAT_ID=os.getenv("TELEGRAM_CHAT_ID","")
