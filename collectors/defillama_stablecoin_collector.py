from datetime import datetime, timezone
from pathlib import Path
import csv
import requests

URL = "https://stablecoins.llama.fi/stablecoins?includePrices=true"

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


def fetch_defillama_stablecoins(output: str) -> dict:
    r = requests.get(URL, timeout=30)
    r.raise_for_status()
    data = r.json()

    assets = data.get("peggedAssets", [])
    total = 0.0

    for asset in assets:
        value = _extract_supply(asset)
        if value is not None:
            total += value

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    row = {field: "" for field in FIELDS}
    row["date"] = today
    row["stablecoin_supply"] = total if total else ""

    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(row)

    return {"output": str(path), "date": today, "stablecoin_supply": total, "asset_count": len(assets)}


def _extract_supply(asset):
    for key in ["circulating", "mcap", "marketCap", "supply"]:
        value = asset.get(key)
        if isinstance(value, dict):
            for k in ["peggedUSD", "usd", "value"]:
                parsed = _to_float(value.get(k))
                if parsed is not None:
                    return parsed
        else:
            parsed = _to_float(value)
            if parsed is not None:
                return parsed
    return None


def _to_float(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None
