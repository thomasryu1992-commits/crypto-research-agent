import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from collectors.defillama_stablecoin_collector import fetch_defillama_stablecoins


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="sample_data/extra_metrics_from_defillama_stablecoins.csv")
    args = parser.parse_args()

    result = fetch_defillama_stablecoins(args.output)

    print("DefiLlama stablecoin fetch completed.")
    print(f"Output: {result['output']}")
    print(f"Date: {result['date']}")
    print(f"Stablecoin supply: {result['stablecoin_supply']}")
    print(f"Asset count: {result['asset_count']}")


if __name__ == "__main__":
    main()
