from __future__ import annotations

from datetime import datetime
from io import StringIO
from pathlib import Path
import re

import pandas as pd
import requests

from core.etf_flow_transformer import transform_etf_flow_csv


FARSIDE_ALL_DATA_URL = "https://farside.co.uk/bitcoin-etf-flow-all-data/"

RAW_COLUMNS = [
    "date",
    "total_btc_etf_netflow",
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
]

ALIASES = {
    "date": ["date"],
    "total_btc_etf_netflow": ["total"],
    "ibit_netflow": ["ibit"],
    "fbtc_netflow": ["fbtc"],
    "gbtc_netflow": ["gbtc"],
    "arkb_netflow": ["arkb"],
    "bitb_netflow": ["bitb"],
    "btco_netflow": ["btco"],
    "hodl_netflow": ["hodl"],
    "brk_netflow": ["brk", "brkb"],
    "ezbc_netflow": ["ezbc"],
    "btc_netflow": ["btc"],
}


def fetch_farside_etf_flow(output_raw: str, output_extra: str | None = None) -> dict:
    html = _fetch_html_with_browser_headers(FARSIDE_ALL_DATA_URL)
    tables = pd.read_html(StringIO(html))

    if not tables:
        raise RuntimeError("No tables found on Farside page.")

    table = _select_table(tables)
    normalized = _normalize(table)

    raw_path = Path(output_raw)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    normalized.to_csv(raw_path, index=False, encoding="utf-8-sig")

    result = {"raw_path": str(raw_path), "rows": len(normalized)}

    if output_extra:
        transform_etf_flow_csv(str(raw_path), output_extra)
        result["extra_path"] = output_extra

    return result


def _fetch_html_with_browser_headers(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": "https://farside.co.uk/",
    }

    session = requests.Session()
    response = session.get(url, headers=headers, timeout=30)

    if response.status_code == 403:
        raise RuntimeError(
            "Farside returned HTTP 403 Forbidden. "
            "The site is blocking automated access from Python. "
            "Use the manual CSV fallback: copy the Farside ETF table into "
            "sample_data/etf_flow_raw_manual.csv, then run "
            "python tools/build_extra_metrics_from_etf_csv.py "
            "--input sample_data/etf_flow_raw_manual.csv "
            "--output sample_data/extra_metrics_from_farside.csv"
        )

    response.raise_for_status()
    return response.text


def _select_table(tables):
    best = None
    best_score = -1

    for table in tables:
        cols = " ".join(_clean_col(c) for c in table.columns)
        score = sum(1 for token in ["date", "ibit", "fbtc", "gbtc", "total"] if token in cols)

        if score > best_score:
            best = table
            best_score = score

    if best is None or best_score < 3:
        raise RuntimeError("Could not identify ETF flow table. Farside table structure may have changed.")

    return best


def _normalize(table):
    df = table.copy()
    df.columns = [_clean_col(c) for c in df.columns]

    output = []

    for _, row in df.iterrows():
        item = {}

        for target, aliases in ALIASES.items():
            col = _find_col(df.columns, aliases)

            if col is None:
                item[target] = ""
            elif target == "date":
                item[target] = _parse_date(row.get(col))
            else:
                item[target] = _usdm_to_usd(row.get(col))

        if item.get("date"):
            output.append({column: item.get(column, "") for column in RAW_COLUMNS})

    result = pd.DataFrame(output)

    if result.empty:
        raise RuntimeError("ETF table parsed but no valid rows produced.")

    return result.drop_duplicates(subset=["date"]).sort_values("date")


def _clean_col(value):
    text = str(value).strip().lower().replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text


def _find_col(columns, aliases):
    for alias in aliases:
        alias = _clean_col(alias)

        for col in columns:
            if _clean_col(col) == alias:
                return col

        for col in columns:
            if alias in _clean_col(col):
                return col

    return None


def _parse_date(value):
    if value is None:
        return ""

    text = str(value).strip()

    if not text or text.lower() in ["nan", "none"]:
        return ""

    for fmt in [
        "%Y-%m-%d",
        "%d %b %Y",
        "%d %B %Y",
        "%b %d %Y",
        "%B %d %Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
    ]:
        try:
            candidate = text[:10] if fmt == "%Y-%m-%d" else text
            return datetime.strptime(candidate, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass

    parsed = pd.to_datetime(text, errors="coerce")

    if pd.notna(parsed):
        return parsed.strftime("%Y-%m-%d")

    return ""


def _usdm_to_usd(value):
    if value is None:
        return ""

    text = str(value).strip()

    if not text or text == "-" or text.lower() in ["nan", "none"]:
        return ""

    text = text.replace(",", "").replace("$", "").replace(" ", "")

    negative = text.startswith("(") and text.endswith(")")

    if negative:
        text = text[1:-1]

    try:
        usd = float(text) * 1_000_000
        return -usd if negative else usd
    except ValueError:
        return ""
