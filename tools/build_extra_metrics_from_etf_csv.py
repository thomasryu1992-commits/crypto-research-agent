import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from core.etf_flow_transformer import transform_etf_flow_csv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Raw ETF flow CSV path")
    parser.add_argument("--output", required=True, help="Output extra metrics CSV path")
    args = parser.parse_args()

    rows = transform_etf_flow_csv(args.input, args.output)

    print("ETF flow transformation completed.")
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"Rows: {len(rows)}")


if __name__ == "__main__":
    main()
