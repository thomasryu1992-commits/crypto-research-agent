from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"
BACKTEST_DIR = DATA_DIR / "backtests"
REPORT_DIR = DATA_DIR / "reports"
PROCESSED_DIR = DATA_DIR / "processed"

DAILY_FORWARD_WINDOWS = [1, 7, 30]
WEEKLY_FORWARD_WINDOWS = [1, 4, 12]

SCORE_THRESHOLDS = {
    "strong_bullish": 0.55,
    "bullish": 0.25,
    "neutral_upper": 0.25,
    "neutral_lower": -0.25,
    "bearish": -0.25,
    "strong_bearish": -0.55,
}
