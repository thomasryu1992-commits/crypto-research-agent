import argparse
import csv
import json
from pathlib import Path


def analyze_results(results_path: str, window: int) -> dict:
    rows = []

    with open(results_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    forward_col = f"forward_return_{window}"

    analysis = {
        "results_path": results_path,
        "window": window,
        "signal_quality": _group(rows, "signal_quality", forward_col),
        "signal_quality_label": _group(rows, "signal_quality_label", forward_col),
        "signal_timing": _group(rows, "signal_timing", forward_col),
        "signal_timing_label": _group(rows, "signal_timing_label", forward_col),
        "bias": _group(rows, "bias", forward_col),
        "scenario": _group(rows, "scenario", forward_col),
    }

    return analysis


def _group(rows, key, value_col):
    grouped = {}

    for row in rows:
        group_key = row.get(key) or "Unknown"
        value = _to_float(row.get(value_col))

        if value is None:
            continue

        grouped.setdefault(group_key, []).append(value)

    result = {}

    for group_key, values in grouped.items():
        result[group_key] = {
            "count": len(values),
            "avg_forward_return": sum(values) / len(values) if values else None,
            "positive_rate": sum(1 for v in values if v > 0) / len(values) if values else None,
            "negative_rate": sum(1 for v in values if v < 0) / len(values) if values else None,
        }

    return result


def _to_float(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", required=True)
    parser.add_argument("--window", type=int, default=7)
    parser.add_argument("--output", default="data/backtests/signal_quality_analysis.json")
    args = parser.parse_args()

    analysis = analyze_results(args.results, args.window)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Signal quality analysis completed.")
    print(f"Input: {args.results}")
    print(f"Output: {output_path}")
    print(json.dumps(analysis, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
