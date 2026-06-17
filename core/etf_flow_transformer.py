import csv
from pathlib import Path


EXTRA_METRICS_FIELDS = [
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


def transform_etf_flow_csv(input_path: str, output_path: str) -> list[dict]:
    raw_rows = _read_raw_etf_csv(input_path)
    raw_rows.sort(key=lambda r: r["date"])

    transformed = []

    for i, row in enumerate(raw_rows):
        total_flow = row.get("total_btc_etf_netflow")
        ibit_flow = row.get("ibit_netflow")

        etf_5d_netflow = _rolling_sum(raw_rows, i, "total_btc_etf_netflow", window=5)
        consecutive_inflow_days = _consecutive_days(raw_rows, i, direction="positive")
        consecutive_outflow_days = _consecutive_days(raw_rows, i, direction="negative")

        transformed.append({
            "date": row["date"],
            "total_btc_etf_netflow": total_flow,
            "ibit_netflow": ibit_flow,
            "etf_5d_netflow": etf_5d_netflow,
            "etf_consecutive_inflow_days": consecutive_inflow_days,
            "etf_consecutive_outflow_days": consecutive_outflow_days,
            "exchange_netflow": None,
            "exchange_reserve": None,
            "stablecoin_supply": None,
            "stablecoin_exchange_reserve": None,
            "mvrv": None,
            "sopr": None,
            "active_addresses": None,
            "tx_count": None,
        })

    _write_extra_metrics_csv(output_path, transformed)
    return transformed


def _read_raw_etf_csv(path: str) -> list[dict]:
    rows = []

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        if "date" not in reader.fieldnames:
            raise ValueError("ETF raw CSV must include a 'date' column.")

        for raw in reader:
            date = raw.get("date")

            if not date:
                continue

            total = _first_available_number(
                raw,
                [
                    "total_btc_etf_netflow",
                    "total_netflow",
                    "total",
                    "netflow",
                    "net_flow",
                ],
            )

            ibit = _first_available_number(
                raw,
                [
                    "ibit_netflow",
                    "blackrock_ibit_netflow",
                    "blackrock",
                    "ibit",
                ],
            )

            if total is None:
                total = _sum_known_issuer_flows(raw)

            rows.append({
                "date": date,
                "total_btc_etf_netflow": total,
                "ibit_netflow": ibit,
            })

    return rows


def _first_available_number(raw: dict, keys: list[str]):
    for key in keys:
        if key in raw and raw.get(key) not in [None, ""]:
            return _to_float(raw.get(key))
    return None


def _sum_known_issuer_flows(raw: dict):
    issuer_keys = [
        "ibit_netflow",
        "fbtc_netflow",
        "gbtc_netflow",
        "arkb_netflow",
        "bitb_netflow",
        "btco_netflow",
        "hodl_netflow",
        "brk_netflow",
        "ezbc_netflow",
        "btc_netflow",
        "ibit",
        "fbtc",
        "gbtc",
        "arkb",
        "bitb",
        "btco",
        "hodl",
        "brk",
        "ezbc",
        "btc",
    ]

    values = []

    for key in issuer_keys:
        if key in raw:
            value = _to_float(raw.get(key))
            if value is not None:
                values.append(value)

    if not values:
        return None

    return sum(values)


def _rolling_sum(rows: list[dict], index: int, key: str, window: int):
    start = max(0, index - window + 1)
    values = [
        rows[i].get(key)
        for i in range(start, index + 1)
        if rows[i].get(key) is not None
    ]

    if not values:
        return None

    return sum(values)


def _consecutive_days(rows: list[dict], index: int, direction: str) -> int:
    count = 0

    for i in range(index, -1, -1):
        value = rows[i].get("total_btc_etf_netflow")

        if value is None:
            break

        if direction == "positive" and value > 0:
            count += 1
        elif direction == "negative" and value < 0:
            count += 1
        else:
            break

    return count


def _write_extra_metrics_csv(path: str, rows: list[dict]):
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=EXTRA_METRICS_FIELDS)
        writer.writeheader()

        for row in rows:
            writer.writerow({
                field: _format_value(row.get(field))
                for field in EXTRA_METRICS_FIELDS
            })


def _format_value(value):
    if value is None:
        return ""
    return value


def _to_float(value):
    try:
        if value is None:
            return None

        text = str(value).strip()

        if text == "":
            return None

        text = (
            text.replace(",", "")
            .replace("$", "")
            .replace(" ", "")
        )

        # Some sources use parentheses for negative values.
        if text.startswith("(") and text.endswith(")"):
            text = "-" + text[1:-1]

        return float(text)

    except (TypeError, ValueError):
        return None
