def build_features(rows: list[dict], timeframe: str) -> list[dict]:
    enriched = []

    for i, row in enumerate(rows):
        item = dict(row)

        # Basic returns
        item["return_1"] = _pct_change(_get(rows, i - 1, "close"), row.get("close"))
        item["return_3"] = _pct_change(_get(rows, i - 3, "close"), row.get("close"))
        item["return_7"] = _pct_change(_get(rows, i - 7, "close"), row.get("close"))
        item["return_14"] = _pct_change(_get(rows, i - 14, "close"), row.get("close"))
        item["return_30"] = _pct_change(_get(rows, i - 30, "close"), row.get("close"))

        # Rolling changes
        item["volume_change_1"] = _pct_change(_get(rows, i - 1, "volume"), row.get("volume"))
        item["volume_change_3"] = _pct_change(_rolling_avg(rows, i - 3, i, "volume"), row.get("volume"))
        item["volume_change_7"] = _pct_change(_rolling_avg(rows, i - 7, i, "volume"), row.get("volume"))

        item["oi_change_1"] = _pct_change(_get(rows, i - 1, "open_interest_close"), row.get("open_interest_close"))
        item["oi_change_3"] = _pct_change(_get(rows, i - 3, "open_interest_close"), row.get("open_interest_close"))
        item["oi_change_7"] = _pct_change(_get(rows, i - 7, "open_interest_close"), row.get("open_interest_close"))

        item["cvd_change_1"] = _absolute_change(_get(rows, i - 1, "cvd"), row.get("cvd"))
        item["cvd_change_3"] = _absolute_change(_get(rows, i - 3, "cvd"), row.get("cvd"))
        item["cvd_change_7"] = _absolute_change(_get(rows, i - 7, "cvd"), row.get("cvd"))

        item["range_percent"] = _range_percent(row.get("high"), row.get("low"), row.get("close"))

        # External metric changes
        item["exchange_reserve_change_7"] = _pct_change(_get(rows, i - 7, "exchange_reserve"), row.get("exchange_reserve"))
        item["stablecoin_supply_change_7"] = _pct_change(_get(rows, i - 7, "stablecoin_supply"), row.get("stablecoin_supply"))
        item["stablecoin_exchange_reserve_change_7"] = _pct_change(_get(rows, i - 7, "stablecoin_exchange_reserve"), row.get("stablecoin_exchange_reserve"))
        item["active_addresses_change_7"] = _pct_change(_get(rows, i - 7, "active_addresses"), row.get("active_addresses"))
        item["tx_count_change_7"] = _pct_change(_get(rows, i - 7, "tx_count"), row.get("tx_count"))

        enriched.append(item)

    percentile_fields = [
        "volume_change_1",
        "volume_change_3",
        "volume_change_7",
        "oi_change_1",
        "oi_change_3",
        "oi_change_7",
        "cvd_change_1",
        "cvd_change_3",
        "cvd_change_7",
        "range_percent",
        "total_btc_etf_netflow",
        "ibit_netflow",
        "etf_5d_netflow",
        "exchange_netflow",
        "exchange_reserve_change_7",
        "stablecoin_supply_change_7",
        "stablecoin_exchange_reserve_change_7",
        "mvrv",
        "sopr",
        "active_addresses_change_7",
        "tx_count_change_7",
    ]

    for field in percentile_fields:
        _add_rolling_percentile(enriched, field, lookback=90)

    return enriched


def _get(rows: list[dict], index: int, key: str):
    if index < 0 or index >= len(rows):
        return None
    return rows[index].get(key)


def _rolling_avg(rows: list[dict], start_index: int, end_index: int, key: str):
    if start_index < 0:
        return None

    values = []

    for idx in range(start_index, end_index):
        value = _get(rows, idx, key)
        if value is not None:
            values.append(value)

    if not values:
        return None

    return sum(values) / len(values)


def _pct_change(old, new):
    try:
        if old is None or new is None or float(old) == 0:
            return None
        return ((float(new) - float(old)) / float(old)) * 100
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def _absolute_change(old, new):
    try:
        if old is None or new is None:
            return None
        return float(new) - float(old)
    except (TypeError, ValueError):
        return None


def _range_percent(high, low, close):
    try:
        if high is None or low is None or close is None or float(close) == 0:
            return None
        return ((float(high) - float(low)) / float(close)) * 100
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def _add_rolling_percentile(rows: list[dict], field: str, lookback: int = 90):
    percentile_key = f"{field}_pctile"

    for i, row in enumerate(rows):
        value = row.get(field)

        if value is None or i < 10:
            row[percentile_key] = None
            continue

        start = max(0, i - lookback)
        history = [
            r.get(field)
            for r in rows[start:i]
            if r.get(field) is not None
        ]

        if len(history) < 10:
            row[percentile_key] = None
            continue

        lower_or_equal = sum(1 for h in history if h <= value)
        row[percentile_key] = lower_or_equal / len(history)
