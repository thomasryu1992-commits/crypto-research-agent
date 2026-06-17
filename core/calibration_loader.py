import json
from pathlib import Path


DEFAULT_CALIBRATION = {
    "daily": {
        "bullish_threshold": 0.45,
        "constructive_threshold": 0.25,
        "risk_off_threshold": -0.25,
        "bearish_threshold": -0.45,
        "market_confirm_threshold": 0.15,
        "market_bearish_confirm_threshold": -0.15,
    },
    "weekly": {
        "bullish_threshold": 0.35,
        "constructive_threshold": 0.20,
        "risk_off_threshold": -0.25,
        "bearish_threshold": -0.60,
        "market_confirm_threshold": 0.20,
        "market_bearish_confirm_threshold": -0.30,
    },
}


def load_calibration(path: str | None = None) -> dict:
    if not path:
        return DEFAULT_CALIBRATION

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Calibration file not found: {path}")

    data = json.loads(p.read_text(encoding="utf-8"))
    calibration = {}

    for timeframe in ["daily", "weekly"]:
        merged = DEFAULT_CALIBRATION[timeframe].copy()

        if timeframe in data:
            merged.update(data[timeframe])
        else:
            merged.update({k: v for k, v in data.items() if k in merged})

        calibration[timeframe] = merged

    return calibration


def get_timeframe_calibration(calibration: dict | None, timeframe: str) -> dict:
    if calibration is None:
        calibration = DEFAULT_CALIBRATION

    return calibration.get(timeframe, DEFAULT_CALIBRATION.get(timeframe, DEFAULT_CALIBRATION["daily"]))
