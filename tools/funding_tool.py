import requests
from config import BINANCE_FUTURES_BASE_URL

def get_funding_rate(symbol:str)->dict:
    try:
        r=requests.get(f"{BINANCE_FUTURES_BASE_URL}/fapi/v1/premiumIndex",params={"symbol":symbol},timeout=10); r.raise_for_status(); d=r.json()
        return {"symbol":symbol,"funding_rate":_f(d.get("lastFundingRate")),"next_funding_time":d.get("nextFundingTime"),"mark_price":_f(d.get("markPrice")),"index_price":_f(d.get("indexPrice"))}
    except requests.RequestException as e: return {"symbol":symbol,"error":str(e)}
def _f(v):
    try: return float(v)
    except: return None
