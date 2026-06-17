import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from collectors.farside_etf_collector import fetch_farside_etf_flow


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-raw", default="sample_data/etf_flow_raw_farside.csv")
    parser.add_argument("--output-extra", default="sample_data/extra_metrics_from_farside.csv")
    args = parser.parse_args()

    result = fetch_farside_etf_flow(args.output_raw, args.output_extra)

    print("Farside ETF flow fetch completed.")
    print(f"Raw CSV: {result['raw_path']}")
    print(f"Extra metrics CSV: {result.get('extra_path')}")
    print(f"Rows: {result['rows']}")


if __name__ == "__main__":
    main()
