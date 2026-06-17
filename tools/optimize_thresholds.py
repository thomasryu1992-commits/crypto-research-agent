import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from config import BACKTEST_DIR
from core.csv_loader import load_tradingview_csv
from core.extra_metrics_loader import load_extra_metrics_csv, merge_extra_metrics
from metrics.feature_builder import build_features
from metrics.scoring_engine import score_row
from backtesting.threshold_optimizer import optimize_thresholds
from storage.csv_writer import write_csv, write_json


def run_optimizer(csv_path: str, timeframe: str, extra_csv: str | None = None):
    rows = load_tradingview_csv(csv_path)
    extra_by_date = load_extra_metrics_csv(extra_csv)
    rows = merge_extra_metrics(rows, extra_by_date)

    features = build_features(rows, timeframe)
    scored_rows = [score_row(row, timeframe) for row in features]

    primary_window = 4 if timeframe == "weekly" else 7
    results, best_calibration = optimize_thresholds(scored_rows, timeframe, primary_window)

    BACKTEST_DIR.mkdir(parents=True, exist_ok=True)

    suffix = "with_extra" if extra_csv else "market_only"
    results_path = BACKTEST_DIR / f"btc_{timeframe}_{suffix}_threshold_optimization.csv"
    best_path = BACKTEST_DIR / f"btc_{timeframe}_{suffix}_best_calibration.json"

    write_csv(results_path, results)
    write_json(best_path, best_calibration)

    print("Threshold optimization completed.")
    print(f"Timeframe: {timeframe}")
    print(f"Extra metrics: {extra_csv if extra_csv else 'not provided'}")
    print(f"Candidates tested: {len(results)}")
    print(f"Results CSV: {results_path}")
    print(f"Best calibration JSON: {best_path}")
    print("Best calibration:")
    print(best_calibration)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to TradingView CSV file")
    parser.add_argument("--timeframe", choices=["daily", "weekly"], required=True)
    parser.add_argument("--extra-csv", default=None, help="Optional external metrics CSV")
    args = parser.parse_args()

    run_optimizer(args.csv, args.timeframe, args.extra_csv)


if __name__ == "__main__":
    main()
