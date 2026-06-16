import requests
from config import BINANCE_FUTURES_BASE_URL


def get_funding_rate(symbol: str) -> dict:
    url = f"{BINANCE_FUTURES_BASE_URL}/fapi/v1/premiumIndex"
    params = {"symbol": symbol}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "symbol": symbol,
            "funding_rate": _safe_float(data.get("lastFundingRate")),
            "next_funding_time": data.get("nextFundingTime"),
            "mark_price": _safe_float(data.get("markPrice")),
            "index_price": _safe_float(data.get("indexPrice")),
        }

    except requests.RequestException as e:
        return {"symbol": symbol, "error": str(e)}


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
