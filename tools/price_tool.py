import requests
from config import BINANCE_SPOT_BASE_URL


def get_price_data(symbol: str) -> dict:
    url = f"{BINANCE_SPOT_BASE_URL}/api/v3/ticker/24hr"
    params = {"symbol": symbol}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "symbol": symbol,
            "last_price": _safe_float(data.get("lastPrice")),
            "price_change": _safe_float(data.get("priceChange")),
            "price_change_percent": _safe_float(data.get("priceChangePercent")),
            "high_price": _safe_float(data.get("highPrice")),
            "low_price": _safe_float(data.get("lowPrice")),
            "volume": _safe_float(data.get("volume")),
            "quote_volume": _safe_float(data.get("quoteVolume")),
        }
    except requests.RequestException as e:
        return {"symbol": symbol, "error": str(e)}


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
