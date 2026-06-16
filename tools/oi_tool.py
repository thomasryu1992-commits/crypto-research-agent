import requests
from config import BINANCE_FUTURES_BASE_URL


def get_open_interest(symbol: str) -> dict:
    url = f"{BINANCE_FUTURES_BASE_URL}/fapi/v1/openInterest"
    params = {"symbol": symbol}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "symbol": symbol,
            "open_interest": _safe_float(data.get("openInterest")),
            "time": data.get("time"),
        }

    except requests.RequestException as e:
        return {"symbol": symbol, "error": str(e)}


def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
