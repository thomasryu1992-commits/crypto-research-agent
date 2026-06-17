import requests
from config import BINANCE_FUTURES_BASE_URL

def get_recent_futures_candles(symbol:str,interval:str="1h",limit:int=24)->list[dict]:
    try:
        r=requests.get(f"{BINANCE_FUTURES_BASE_URL}/fapi/v1/klines",params={"symbol":symbol,"interval":interval,"limit":limit},timeout=10); r.raise_for_status()
        return [{"open_time":i[0],"open":_f(i[1]),"high":_f(i[2]),"low":_f(i[3]),"close":_f(i[4]),"volume":_f(i[5]),"close_time":i[6]} for i in r.json()]
    except requests.RequestException: return []
def summarize_candles(candles:list[dict])->dict:
    if not candles: return {"available":False,"message":"캔들 데이터를 가져오지 못했습니다."}
    first,last=candles[0],candles[-1]
    highs=[c.get("high") for c in candles if c.get("high") is not None]; lows=[c.get("low") for c in candles if c.get("low") is not None]; vols=[c.get("volume") for c in candles if c.get("volume") is not None]
    bullish=sum(1 for c in candles if c.get("close") is not None and c.get("open") is not None and c["close"]>c["open"]); bearish=sum(1 for c in candles if c.get("close") is not None and c.get("open") is not None and c["close"]<c["open"])
    ch=_pct(first.get("close"),last.get("close")); trend="unknown" if ch is None else "uptrend" if ch>1 else "downtrend" if ch<-1 else "range"
    return {"available":True,"candle_count":len(candles),"timeframe":"recent_1h_candles","first_close":first.get("close"),"last_close":last.get("close"),"change_percent":ch,"highest_high":max(highs,default=None),"lowest_low":min(lows,default=None),"total_volume":sum(vols),"bullish_candles":bullish,"bearish_candles":bearish,"trend":trend}
def _f(v):
    try: return float(v)
    except: return None
def _pct(o,n):
    try:
        if o is None or n is None or float(o)==0: return None
        return ((float(n)-float(o))/float(o))*100
    except: return None
