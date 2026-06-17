from metrics.external_scoring import score_external_categories


def score_row(row: dict, timeframe: str) -> dict:
    if timeframe == "weekly":
        market_score = _score_market_structure_weekly(row)
        derivatives_score = _score_derivatives_weekly(row)
        cvd_score = _score_cvd_weekly(row)
        volume_score = _score_volume_weekly(row)

        base_weights = {
            "market_structure": 0.30,
            "derivatives": 0.15,
            "cvd": 0.15,
            "volume": 0.05,
            "etf": 0.15,
            "exchange": 0.10,
            "stablecoin": 0.05,
            "valuation": 0.03,
            "network": 0.02,
        }
    else:
        market_score = _score_market_structure_daily(row)
        derivatives_score = _score_derivatives_daily(row)
        cvd_score = _score_cvd_daily(row)
        volume_score = _score_volume_daily(row)

        base_weights = {
            "market_structure": 0.20,
            "derivatives": 0.20,
            "cvd": 0.15,
            "volume": 0.05,
            "etf": 0.20,
            "exchange": 0.10,
            "stablecoin": 0.05,
            "valuation": 0.03,
            "network": 0.02,
        }

    external = score_external_categories(row, timeframe)

    raw_scores = {
        "market_structure": market_score,
        "derivatives": derivatives_score,
        "cvd": cvd_score,
        "volume": volume_score,
        "etf": external["etf_institutional_flow_score"],
        "exchange": external["exchange_flow_score"],
        "stablecoin": external["stablecoin_liquidity_score"],
        "valuation": external["valuation_cycle_score"],
        "network": external["network_activity_score"],
    }

    active_scores = {}
    for key, value in raw_scores.items():
        # External categories with missing data return 0.
        # We keep them active only if the underlying category has data.
        if key in ["etf", "exchange", "stablecoin", "valuation", "network"]:
            if _has_external_data_for_category(row, key):
                active_scores[key] = value
        else:
            active_scores[key] = value

    final_score = _weighted_average(active_scores, base_weights)

    return {
        "date": row.get("date"),
        "close": row.get("close"),
        "market_structure_score": round(market_score, 4),
        "derivatives_positioning_score": round(derivatives_score, 4),
        "cvd_flow_score": round(cvd_score, 4),
        "volume_score": round(volume_score, 4),
        **external,
        "final_score": round(final_score, 4),
        "metric_context": {
            "return_1": row.get("return_1"),
            "return_3": row.get("return_3"),
            "return_7": row.get("return_7"),
            "return_14": row.get("return_14"),
            "return_30": row.get("return_30"),
            "rsi": row.get("rsi"),
            "oi_change_1": row.get("oi_change_1"),
            "oi_change_3": row.get("oi_change_3"),
            "oi_change_7": row.get("oi_change_7"),
            "oi_change_3_pctile": row.get("oi_change_3_pctile"),
            "oi_change_7_pctile": row.get("oi_change_7_pctile"),
            "cvd_change_1": row.get("cvd_change_1"),
            "cvd_change_3": row.get("cvd_change_3"),
            "cvd_change_7": row.get("cvd_change_7"),
            "cvd_change_3_pctile": row.get("cvd_change_3_pctile"),
            "cvd_change_7_pctile": row.get("cvd_change_7_pctile"),
            "volume_change_1": row.get("volume_change_1"),
            "volume_change_3": row.get("volume_change_3"),
            "volume_change_7": row.get("volume_change_7"),
            "volume_change_3_pctile": row.get("volume_change_3_pctile"),
            "volume_change_7_pctile": row.get("volume_change_7_pctile"),
            "open_interest_close": row.get("open_interest_close"),
            "range_percent": row.get("range_percent"),
            "range_percent_pctile": row.get("range_percent_pctile"),
            "total_btc_etf_netflow": row.get("total_btc_etf_netflow"),
            "ibit_netflow": row.get("ibit_netflow"),
            "etf_5d_netflow": row.get("etf_5d_netflow"),
            "exchange_netflow": row.get("exchange_netflow"),
            "exchange_reserve": row.get("exchange_reserve"),
            "stablecoin_supply": row.get("stablecoin_supply"),
            "stablecoin_exchange_reserve": row.get("stablecoin_exchange_reserve"),
            "mvrv": row.get("mvrv"),
            "sopr": row.get("sopr"),
            "active_addresses": row.get("active_addresses"),
            "tx_count": row.get("tx_count"),
        },
    }


def _weighted_average(scores: dict, weights: dict) -> float:
    numerator = 0.0
    denominator = 0.0

    for key, score in scores.items():
        weight = weights.get(key, 0.0)
        numerator += score * weight
        denominator += weight

    if denominator == 0:
        return 0.0

    return numerator / denominator


def _has_external_data_for_category(row: dict, category: str) -> bool:
    fields = {
        "etf": [
            "total_btc_etf_netflow",
            "ibit_netflow",
            "etf_5d_netflow",
            "etf_consecutive_inflow_days",
            "etf_consecutive_outflow_days",
        ],
        "exchange": [
            "exchange_netflow",
            "exchange_reserve",
            "exchange_reserve_change_7",
        ],
        "stablecoin": [
            "stablecoin_supply",
            "stablecoin_exchange_reserve",
            "stablecoin_supply_change_7",
            "stablecoin_exchange_reserve_change_7",
        ],
        "valuation": [
            "mvrv",
            "sopr",
        ],
        "network": [
            "active_addresses",
            "tx_count",
            "active_addresses_change_7",
            "tx_count_change_7",
        ],
    }

    return any(row.get(field) is not None for field in fields.get(category, []))


# -----------------------------
# Daily scoring
# -----------------------------

def _score_market_structure_daily(row: dict) -> float:
    r1 = row.get("return_1")
    r3 = row.get("return_3")
    r7 = row.get("return_7")
    rsi = row.get("rsi")

    score = 0.0

    if r1 is not None:
        score += _clip(r1 / 4) * 0.20

    if r3 is not None:
        score += _clip(r3 / 8) * 0.35

    if r7 is not None:
        score += _clip(r7 / 14) * 0.30

    if rsi is not None:
        if rsi >= 78:
            score += -0.30
        elif rsi >= 70:
            score += -0.15
        elif rsi <= 24:
            score += 0.25
        elif rsi <= 32:
            score += 0.10

    return _clip(score)


def _score_derivatives_daily(row: dict) -> float:
    r3 = row.get("return_3")
    oi3 = row.get("oi_change_3")
    oi_pct = row.get("oi_change_3_pctile")

    if r3 is None or oi3 is None:
        return 0.0

    oi_extreme_high = oi_pct is not None and oi_pct >= 0.85
    oi_extreme_low = oi_pct is not None and oi_pct <= 0.15

    if r3 < -2 and oi3 > 0 and oi_extreme_high:
        return -0.70

    if r3 < 0 and oi3 > 0:
        return -0.45

    if r3 < 0 and oi3 < 0:
        return -0.10

    if r3 > 0 and oi3 > 0 and not oi_extreme_high:
        return 0.35

    if r3 > 0 and oi3 > 0 and oi_extreme_high:
        return -0.15

    if r3 > 0 and oi3 < 0:
        return 0.10

    if oi_extreme_low:
        return 0.05

    return 0.0


def _score_cvd_daily(row: dict) -> float:
    r3 = row.get("return_3")
    cvd3 = row.get("cvd_change_3")
    cvd_pct = row.get("cvd_change_3_pctile")

    if r3 is None or cvd3 is None:
        return 0.0

    strong_buy = cvd_pct is not None and cvd_pct >= 0.75
    strong_sell = cvd_pct is not None and cvd_pct <= 0.25

    if cvd3 > 0 and r3 > 0 and strong_buy:
        return 0.45

    if cvd3 > 0 and r3 <= 0:
        return 0.05

    if cvd3 < 0 and r3 < 0 and strong_sell:
        return -0.45

    if cvd3 < 0 and r3 >= 0:
        return 0.05

    if cvd3 > 0 and r3 > 0:
        return 0.25

    if cvd3 < 0 and r3 < 0:
        return -0.25

    return 0.0


def _score_volume_daily(row: dict) -> float:
    vol3 = row.get("volume_change_3")
    vol_pct = row.get("volume_change_3_pctile")
    r3 = row.get("return_3")

    if vol3 is None or r3 is None:
        return 0.0

    high_volume = vol_pct is not None and vol_pct >= 0.75

    if high_volume and r3 > 2:
        return 0.25

    if high_volume and r3 < -2:
        return -0.25

    if vol3 < -20:
        return -0.05

    return 0.0


# -----------------------------
# Weekly scoring
# -----------------------------

def _score_market_structure_weekly(row: dict) -> float:
    r1 = row.get("return_1")
    r3 = row.get("return_3")
    r7 = row.get("return_7")
    rsi = row.get("rsi")

    score = 0.0

    if r1 is not None:
        score += _clip(r1 / 8) * 0.25

    if r3 is not None:
        score += _clip(r3 / 18) * 0.35

    if r7 is not None:
        score += _clip(r7 / 35) * 0.25

    if rsi is not None:
        if rsi >= 82:
            score += -0.25
        elif rsi >= 75:
            score += -0.10
        elif rsi <= 30:
            score += 0.20
        elif rsi <= 40:
            score += 0.10

    return _clip(score)


def _score_derivatives_weekly(row: dict) -> float:
    r1 = row.get("return_1")
    oi1 = row.get("oi_change_1")
    oi_pct = row.get("oi_change_1_pctile")

    if r1 is None or oi1 is None:
        return 0.0

    oi_extreme_high = oi_pct is not None and oi_pct >= 0.85

    if r1 > 0 and oi1 > 0 and not oi_extreme_high:
        return 0.35

    if r1 > 0 and oi1 > 0 and oi_extreme_high:
        return -0.10

    if r1 < 0 and oi1 > 0:
        return -0.40

    if r1 < 0 and oi1 < 0:
        return -0.10

    if r1 > 0 and oi1 < 0:
        return 0.10

    return 0.0


def _score_cvd_weekly(row: dict) -> float:
    r1 = row.get("return_1")
    cvd1 = row.get("cvd_change_1")
    cvd_pct = row.get("cvd_change_1_pctile")

    if r1 is None or cvd1 is None:
        return 0.0

    strong_buy = cvd_pct is not None and cvd_pct >= 0.70
    strong_sell = cvd_pct is not None and cvd_pct <= 0.30

    if cvd1 > 0 and r1 > 0 and strong_buy:
        return 0.45

    if cvd1 < 0 and r1 < 0 and strong_sell:
        return -0.40

    if cvd1 > 0 and r1 > 0:
        return 0.25

    if cvd1 < 0 and r1 < 0:
        return -0.25

    if cvd1 < 0 and r1 > 0:
        return -0.05

    if cvd1 > 0 and r1 < 0:
        return 0.05

    return 0.0


def _score_volume_weekly(row: dict) -> float:
    vol1 = row.get("volume_change_1")
    vol_pct = row.get("volume_change_1_pctile")
    r1 = row.get("return_1")

    if vol1 is None or r1 is None:
        return 0.0

    high_volume = vol_pct is not None and vol_pct >= 0.75

    if high_volume and r1 > 0:
        return 0.20

    if high_volume and r1 < 0:
        return -0.20

    return 0.0


def _clip(value: float, low: float = -1.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))
