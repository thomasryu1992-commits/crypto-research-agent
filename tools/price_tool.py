import requests
from config import BINANCE_SPOT_BASE_URL

def get_price_data(symbol:str)->dict:
    try:
        r=requests.get(f"{BINANCE_SPOT_BASE_URL}/api/v3/ticker/24hr",params={"symbol":symbol},timeout=10); r.raise_for_status(); d=r.json()
        return {"symbol":symbol,"last_price":_f(d.get("lastPrice")),"price_change":_f(d.get("priceChange")),"price_change_percent":_f(d.get("priceChangePercent")),"high_price":_f(d.get("highPrice")),"low_price":_f(d.get("lowPrice")),"volume":_f(d.get("volume")),"quote_volume":_f(d.get("quoteVolume"))}
    except requests.RequestException as e: return {"symbol":symbol,"error":str(e)}
def _f(v):
    try: return float(v)
    except: return None
