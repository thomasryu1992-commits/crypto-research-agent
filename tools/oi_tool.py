import requests
from config import BINANCE_FUTURES_BASE_URL

def get_open_interest(symbol:str)->dict:
    try:
        r=requests.get(f"{BINANCE_FUTURES_BASE_URL}/fapi/v1/openInterest",params={"symbol":symbol},timeout=10); r.raise_for_status(); d=r.json()
        return {"symbol":symbol,"open_interest":_f(d.get("openInterest")),"time":d.get("time")}
    except requests.RequestException as e: return {"symbol":symbol,"error":str(e)}
def _f(v):
    try: return float(v)
    except: return None
