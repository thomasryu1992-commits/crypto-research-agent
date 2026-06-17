import argparse

from config import BACKTEST_DIR, DAILY_FORWARD_WINDOWS, WEEKLY_FORWARD_WINDOWS
from core.csv_loader import load_tradingview_csv
from core.extra_metrics_loader import load_extra_metrics_csv, merge_extra_metrics
from core.calibration_loader import load_calibration
from metrics.feature_builder import build_features
from metrics.scoring_engine import score_row
from scenarios.scenario_engine import classify_scenario
from signals.signal_quality import assign_signal_quality
from backtesting.forward_return_calculator import add_forward_returns
from backtesting.performance_evaluator import evaluate_backtest
from storage.csv_writer import write_csv, write_json


def run_backtest(csv_path: str, timeframe: str, extra_csv: str | None = None, calibration_json: str | None = None):
    rows = load_tradingview_csv(csv_path)
    extra_by_date = load_extra_metrics_csv(extra_csv)
    rows = merge_extra_metrics(rows, extra_by_date)

    calibration = load_calibration(calibration_json)

    features = build_features(rows, timeframe)
    scored_rows = []

    for row in features:
        score = score_row(row, timeframe)
        scenario = classify_scenario(score, timeframe, calibration)
        combined = {**score, **scenario}
        quality = assign_signal_quality(combined, timeframe)
        scored_rows.append({**combined, **quality})

    windows = WEEKLY_FORWARD_WINDOWS if timeframe == "weekly" else DAILY_FORWARD_WINDOWS
    rows_with_forward_returns = add_forward_returns(scored_rows, windows)

    primary_window = 4 if timeframe == "weekly" else 7
    evaluation = evaluate_backtest(rows_with_forward_returns, primary_window)

    suffix = "with_extra" if extra_csv else "market_only"
    calibrated_suffix = "_calibrated" if calibration_json else ""
    output_csv = BACKTEST_DIR / f"btc_{timeframe}_{suffix}{calibrated_suffix}_backtest_results.csv"
    output_json = BACKTEST_DIR / f"btc_{timeframe}_{suffix}{calibrated_suffix}_backtest_summary.json"

    write_csv(output_csv, rows_with_forward_returns)
    write_json(output_json, evaluation)

    print(f"Backtest completed: {timeframe}")
    print(f"Extra metrics: {extra_csv if extra_csv else 'not provided'}")
    print(f"Calibration: {calibration_json if calibration_json else 'default'}")
    print(f"Rows: {len(rows_with_forward_returns)}")
    print(f"Results CSV: {output_csv}")
    print(f"Summary JSON: {output_json}")
    print("Evaluation:")
    print(evaluation)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to TradingView CSV file")
    parser.add_argument("--timeframe", choices=["daily", "weekly"], required=True)
    parser.add_argument("--extra-csv", default=None, help="Optional external metrics CSV")
    parser.add_argument("--calibration-json", default=None, help="Optional calibration JSON")
    args = parser.parse_args()

    run_backtest(args.csv, args.timeframe, args.extra_csv, args.calibration_json)


if __name__ == "__main__":
    main()
