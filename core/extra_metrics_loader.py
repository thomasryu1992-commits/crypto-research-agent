import csv


SUPPORTED_EXTRA_FIELDS = [
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


def load_extra_metrics_csv(path: str | None) -> dict[str, dict]:
    if not path:
        return {}

    by_date = {}

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        if "date" not in reader.fieldnames:
            raise ValueError("extra metrics CSV must include a 'date' column.")

        for raw in reader:
            date = raw.get("date")

            if not date:
                continue

            item = {}

            for field in SUPPORTED_EXTRA_FIELDS:
                item[field] = _to_float(raw.get(field))

            by_date[date] = item

    return by_date


def merge_extra_metrics(rows: list[dict], extra_by_date: dict[str, dict]) -> list[dict]:
    merged = []

    for row in rows:
        item = dict(row)
        extra = extra_by_date.get(row.get("date"), {})

        for field in SUPPORTED_EXTRA_FIELDS:
            item[field] = extra.get(field)

        merged.append(item)

    return merged


def _to_float(value):
    try:
        if value is None or value == "":
            return None
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None
