import argparse

from config import REPORT_DIR
from core.csv_loader import load_tradingview_csv
from core.extra_metrics_loader import load_extra_metrics_csv, merge_extra_metrics
from core.calibration_loader import load_calibration
from metrics.feature_builder import build_features
from metrics.scoring_engine import score_row
from scenarios.scenario_engine import classify_scenario
from signals.signal_quality import assign_signal_quality
from reports.report_builder import build_latest_report


def run_latest_report(csv_path: str, timeframe: str, extra_csv: str | None = None, calibration_json: str | None = None):
    rows = load_tradingview_csv(csv_path)
    extra_by_date = load_extra_metrics_csv(extra_csv)
    rows = merge_extra_metrics(rows, extra_by_date)

    calibration = load_calibration(calibration_json)

    features = build_features(rows, timeframe)
    latest = None

    for row in features:
        score = score_row(row, timeframe)
        scenario = classify_scenario(score, timeframe, calibration)
        combined = {**score, **scenario}
        quality = assign_signal_quality(combined, timeframe)
        latest = {**combined, **quality}

    if latest is None:
        raise RuntimeError("No valid rows found.")

    report = build_latest_report(latest, timeframe)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = "with_extra" if extra_csv else "market_only"
    calibrated_suffix = "_calibrated" if calibration_json else ""
    output_path = REPORT_DIR / f"btc_{timeframe}_{suffix}{calibrated_suffix}_latest_report.txt"
    output_path.write_text(report, encoding="utf-8")

    print(report)
    print()
    print(f"Report saved: {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to TradingView CSV file")
    parser.add_argument("--timeframe", choices=["daily", "weekly"], required=True)
    parser.add_argument("--extra-csv", default=None, help="Optional external metrics CSV")
    parser.add_argument("--calibration-json", default=None, help="Optional calibration JSON")
    args = parser.parse_args()

    run_latest_report(args.csv, args.timeframe, args.extra_csv, args.calibration_json)


if __name__ == "__main__":
    main()
