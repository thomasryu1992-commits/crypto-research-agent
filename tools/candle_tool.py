import requests
from config import BINANCE_FUTURES_BASE_URL


def get_recent_futures_candles(symbol: str, interval: str = "1h", limit: int = 24) -> list[dict]:
    url = f"{BINANCE_FUTURES_BASE_URL}/fapi/v1/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw = response.json()

        candles = []
        for item in raw:
            candles.append({
                "open_time": item[0],
                "open": _safe_float(item[1]),
                "high": _safe_float(item[2]),
                "low": _safe_float(item[3]),
                "close": _safe_float(item[4]),
                "volume": _safe_float(item[5]),
                "close_time": item[6],
            })
        return candles
    except requests.RequestException:
        return []


def summarize_candles(candles: list[dict]) -> dict:
    if not candles:
        return {"available": False, "message": "캔들 데이터를 가져오지 못했습니다."}

    first = candles[0]
    last = candles[-1]
    first_close = first.get("close")
    last_close = last.get("close")
    highs = [c.get("high") for c in candles if c.get("high") is not None]
    lows = [c.get("low") for c in candles if c.get("low") is not None]
    volumes = [c.get("volume") for c in candles if c.get("volume") is not None]

    bullish_count = 0
    bearish_count = 0
    for candle in candles:
        if candle.get("close") is None or candle.get("open") is None:
            continue
        if candle["close"] > candle["open"]:
            bullish_count += 1
        elif candle["close"] < candle["open"]:
            bearish_count += 1

    change_percent = _pct_change(first_close, last_close)

    if change_percent is None:
        trend = "unknown"
    elif change_percent > 1:
        trend = "uptrend"
    elif change_percent < -1:
        trend = "downtrend"
    else:
        trend = "range"

    return {
        "available": True,
        "candle_count": len(candles),
        "timeframe": "recent_1h_candles",
        "first_close": first_close,
        "last_close": last_close,
        "change_percent": change_percent,
        "highest_high": max(highs) if highs else None,
        "lowest_low": min(lows) if lows else None,
        "total_volume": sum(volumes),
        "bullish_candles": bullish_count,
        "bearish_candles": bearish_count,
        "trend": trend,
    }


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _pct_change(old, new):
    try:
        if old is None or new is None or float(old) == 0:
            return None
        return ((float(new) - float(old)) / float(old)) * 100
    except (TypeError, ValueError, ZeroDivisionError):
        return None
