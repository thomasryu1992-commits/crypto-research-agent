import csv
from datetime import datetime, timezone


def load_tradingview_csv(path: str) -> list[dict]:
    rows = []

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)

        for raw in reader:
            if not raw or len(raw) < 5:
                continue

            row = _parse_row(raw)
            if row:
                rows.append(row)

    rows.sort(key=lambda x: x["timestamp"])
    return rows


def _parse_row(raw: list[str]) -> dict | None:
    try:
        timestamp = int(float(raw[0]))
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d")

        return {
            "timestamp": timestamp,
            "date": dt,
            "open": _to_float(raw[1]),
            "high": _to_float(raw[2]),
            "low": _to_float(raw[3]),
            "close": _to_float(raw[4]),
            "volume": _to_float(raw[10]) if len(raw) > 10 else None,
            "rsi": _to_float(raw[11]) if len(raw) > 11 else None,
            "regular_bullish": raw[12] if len(raw) > 12 else "",
            "regular_bearish": raw[16] if len(raw) > 16 else "",
            "open_interest_open": _to_float(raw[20]) if len(raw) > 20 else None,
            "open_interest_high": _to_float(raw[21]) if len(raw) > 21 else None,
            "open_interest_low": _to_float(raw[22]) if len(raw) > 22 else None,
            "open_interest_close": _to_float(raw[23]) if len(raw) > 23 else None,
            "open_interest_sma": _to_float(raw[24]) if len(raw) > 24 else None,
            "cvd": _to_float(raw[25]) if len(raw) > 25 else None,
        }

    except (ValueError, IndexError):
        return None


def _to_float(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None
