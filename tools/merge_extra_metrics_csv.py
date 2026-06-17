import argparse
import csv
from pathlib import Path

FIELDS = [
    "date",
    "total_btc_etf_netflow",
    "ibit_netflow",
    "etf_5d_netflow",
    "etf_consecutive_inflow_days",
    "etf_consecutive_outflow_days",
    "exchange_netflow",
    "exchange_reserve",
    "stablecoin_supply",
    "stablecoin_exchange_reserve",
    "mvrv",
    "sopr",
    "active_addresses",
    "tx_count",
]


def merge_extra_metrics(inputs, output):
    by_date = {}

    for input_path in inputs:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if "date" not in reader.fieldnames:
                raise ValueError(f"{input_path} must include date column.")

            for row in reader:
                date = row.get("date")
                if not date:
                    continue

                current = by_date.setdefault(date, {field: "" for field in FIELDS})
                current["date"] = date

                for field in FIELDS:
                    if field == "date":
                        continue
                    value = row.get(field)
                    if value not in [None, ""]:
                        current[field] = value

    rows = [by_date[d] for d in sorted(by_date)]
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    return {"output": str(path), "rows": len(rows)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    result = merge_extra_metrics(args.inputs, args.output)

    print("Extra metrics merge completed.")
    print(f"Output: {result['output']}")
    print(f"Rows: {result['rows']}")


if __name__ == "__main__":
    main()
