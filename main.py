import argparse

from config import REPORT_DIR

from core.csv_loader import load_tradingview_csv
from core.extra_metrics_loader import load_extra_metrics_csv, merge_extra_metrics
from core.calibration_loader import load_calibration
from core.trading_context_loader import load_trading_context

from metrics.feature_builder import build_features
from metrics.scoring_engine import score_row

from scenarios.scenario_engine import classify_scenario

from signals.signal_quality import assign_signal_quality

from reports.report_builder import build_latest_report
from reports.trading_context_report import build_trading_context_section_with_overlay
from reports.final_summary_report import build_final_summary_section
from reports.output_manager import save_report_outputs
from notifiers.telegram_sender import send_telegram_report


def run_latest_report(
    csv_path: str,
    timeframe: str,
    extra_csv: str | None = None,
    calibration_json: str | None = None,
    trading_context_json: str | None = None,
):
    rows = load_tradingview_csv(csv_path)

    extra_by_date = load_extra_metrics_csv(extra_csv)
    rows = merge_extra_metrics(rows, extra_by_date)

    calibration = load_calibration(calibration_json)

    features = build_features(rows, timeframe)

    latest = None

    for row in features:
        score = score_row(row, timeframe)
        scenario = classify_scenario(score, timeframe, calibration)

        combined = {
            **score,
            **scenario,
        }

        quality = assign_signal_quality(combined, timeframe)

        latest = {
            **combined,
            **quality,
        }

    if latest is None:
        raise RuntimeError("No valid rows found.")

    base_report = build_latest_report(latest, timeframe)

    trading_context = load_trading_context(trading_context_json)

    trading_context_section, overlay = build_trading_context_section_with_overlay(
        trading_context,
        latest,
    )

    final_summary_section = build_final_summary_section(
        overlay,
        trading_context,
    )

    final_report = (
        f"{base_report}\n\n"
        f"{trading_context_section}\n\n"
        f"{final_summary_section}"
    )

    suffix = "with_extra" if extra_csv else "market_only"
    calibrated_suffix = "_calibrated" if calibration_json else ""
    context_suffix = "_with_trading_context" if trading_context else "_no_trading_context"

    saved_paths = save_report_outputs(
        final_report=final_report,
        report_dir=REPORT_DIR,
        timeframe=timeframe,
        suffix=suffix,
        calibrated_suffix=calibrated_suffix,
        context_suffix=context_suffix,
    )

    print(final_report)
    print()
    print("=" * 60)
    print("Report Output Manager")
    print("=" * 60)
    print(f"Latest TXT: {saved_paths.get('latest_txt_path')}")
    print(f"Latest MD: {saved_paths.get('latest_md_path')}")
    print(f"Archive TXT: {saved_paths.get('archive_txt_path')}")
    print(f"Archive MD: {saved_paths.get('archive_md_path')}")
    print(f"Simple Latest MD: {saved_paths.get('latest_simple_md_path')}")
    print(f"Telegram Summary: {saved_paths.get('telegram_summary_path')}")

    try:
        telegram_result = send_telegram_report(
            saved_paths.get("telegram_summary_path")
        )

        print()
        print("=" * 60)
        print("Telegram Sender")
        print("=" * 60)

        if telegram_result.get("sent"):
            print(f"Telegram report sent successfully. chunks={telegram_result.get('chunks')}")
        else:
            print(telegram_result.get("message"))

    except Exception as e:
        print()
        print("=" * 60)
        print("Telegram Sender Error")
        print("=" * 60)
        print(f"Telegram 전송 중 문제가 발생했습니다: {e}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--csv",
        required=True,
        help="Path to TradingView CSV file",
    )

    parser.add_argument(
        "--timeframe",
        choices=["daily", "weekly"],
        required=True,
    )

    parser.add_argument(
        "--extra-csv",
        default=None,
        help="Optional external metrics CSV",
    )

    parser.add_argument(
        "--calibration-json",
        default=None,
        help="Optional calibration JSON",
    )

    parser.add_argument(
        "--trading-context-json",
        default=None,
        help="Optional TradingBot_V33 latest_btc_research_context.json path",
    )

    args = parser.parse_args()

    run_latest_report(
        csv_path=args.csv,
        timeframe=args.timeframe,
        extra_csv=args.extra_csv,
        calibration_json=args.calibration_json,
        trading_context_json=args.trading_context_json,
    )


if __name__ == "__main__":
    main()