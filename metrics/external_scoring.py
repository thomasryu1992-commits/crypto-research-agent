def score_external_categories(row: dict, timeframe: str) -> dict:
    etf_score = _score_etf_flow(row, timeframe)
    exchange_score = _score_exchange_flow(row, timeframe)
    stablecoin_score = _score_stablecoin_liquidity(row, timeframe)
    valuation_score = _score_valuation_cycle(row, timeframe)
    network_score = _score_network_activity(row, timeframe)

    return {
        "etf_institutional_flow_score": round(etf_score, 4),
        "exchange_flow_score": round(exchange_score, 4),
        "stablecoin_liquidity_score": round(stablecoin_score, 4),
        "valuation_cycle_score": round(valuation_score, 4),
        "network_activity_score": round(network_score, 4),
    }


def _score_etf_flow(row: dict, timeframe: str) -> float:
    total_flow = row.get("total_btc_etf_netflow")
    ibit_flow = row.get("ibit_netflow")
    etf_5d = row.get("etf_5d_netflow")
    consecutive_in = row.get("etf_consecutive_inflow_days")
    consecutive_out = row.get("etf_consecutive_outflow_days")

    total_pct = row.get("total_btc_etf_netflow_pctile")
    ibit_pct = row.get("ibit_netflow_pctile")
    etf_5d_pct = row.get("etf_5d_netflow_pctile")

    score = 0.0
    used = 0

    if total_flow is not None:
        used += 1
        if total_flow > 0:
            score += _percentile_to_score(total_pct, fallback=0.25)
        elif total_flow < 0:
            score -= _percentile_to_score(1 - total_pct if total_pct is not None else None, fallback=0.25)

    if ibit_flow is not None:
        used += 1
        if ibit_flow > 0:
            score += 0.7 * _percentile_to_score(ibit_pct, fallback=0.20)
        elif ibit_flow < 0:
            score -= 0.7 * _percentile_to_score(1 - ibit_pct if ibit_pct is not None else None, fallback=0.20)

    if etf_5d is not None:
        used += 1
        if etf_5d > 0:
            score += 1.2 * _percentile_to_score(etf_5d_pct, fallback=0.30)
        elif etf_5d < 0:
            score -= 1.2 * _percentile_to_score(1 - etf_5d_pct if etf_5d_pct is not None else None, fallback=0.30)

    if consecutive_in is not None and consecutive_in >= 3:
        score += min(0.30, consecutive_in * 0.04)

    if consecutive_out is not None and consecutive_out >= 3:
        score -= min(0.30, consecutive_out * 0.04)

    if used == 0 and consecutive_in is None and consecutive_out is None:
        return 0.0

    return _clip(score / max(1, used))


def _score_exchange_flow(row: dict, timeframe: str) -> float:
    netflow = row.get("exchange_netflow")
    reserve_change = row.get("exchange_reserve_change_7")
    netflow_pct = row.get("exchange_netflow_pctile")

    score = 0.0
    used = 0

    # BTC exchange netflow: positive netflow means BTC moves into exchanges -> sell pressure.
    if netflow is not None:
        used += 1
        if netflow > 0:
            score -= _percentile_to_score(netflow_pct, fallback=0.35)
        elif netflow < 0:
            score += _percentile_to_score(1 - netflow_pct if netflow_pct is not None else None, fallback=0.35)

    # Exchange reserve falling is usually constructive.
    if reserve_change is not None:
        used += 1
        if reserve_change < 0:
            score += min(0.40, abs(reserve_change) / 5)
        elif reserve_change > 0:
            score -= min(0.40, abs(reserve_change) / 5)

    if used == 0:
        return 0.0

    return _clip(score / used)


def _score_stablecoin_liquidity(row: dict, timeframe: str) -> float:
    supply_change = row.get("stablecoin_supply_change_7")
    exchange_reserve_change = row.get("stablecoin_exchange_reserve_change_7")
    reserve = row.get("stablecoin_exchange_reserve")

    score = 0.0
    used = 0

    if supply_change is not None:
        used += 1
        if supply_change > 0:
            score += min(0.40, supply_change / 5)
        elif supply_change < 0:
            score -= min(0.40, abs(supply_change) / 5)

    if exchange_reserve_change is not None:
        used += 1
        if exchange_reserve_change > 0:
            score += min(0.45, exchange_reserve_change / 5)
        elif exchange_reserve_change < 0:
            score -= min(0.45, abs(exchange_reserve_change) / 5)

    if reserve is not None:
        used += 1
        # Reserve absolute value has no universal meaning without history,
        # so use percentile if available.
        pct = row.get("stablecoin_exchange_reserve_change_7_pctile")
        if pct is not None:
            score += (pct - 0.5) * 0.4

    if used == 0:
        return 0.0

    return _clip(score / used)


def _score_valuation_cycle(row: dict, timeframe: str) -> float:
    mvrv = row.get("mvrv")
    sopr = row.get("sopr")

    score = 0.0
    used = 0

    if mvrv is not None:
        used += 1
        if mvrv >= 3.5:
            score -= 0.55
        elif mvrv >= 2.5:
            score -= 0.30
        elif mvrv <= 1.0:
            score += 0.45
        elif mvrv <= 1.5:
            score += 0.25
        else:
            score += 0.05

    if sopr is not None:
        used += 1
        if sopr > 1.08:
            score -= 0.25
        elif sopr > 1.00:
            score += 0.10
        elif sopr < 0.96:
            score += 0.20
        else:
            score += 0.00

    if used == 0:
        return 0.0

    return _clip(score / used)


def _score_network_activity(row: dict, timeframe: str) -> float:
    active_change = row.get("active_addresses_change_7")
    tx_change = row.get("tx_count_change_7")

    score = 0.0
    used = 0

    if active_change is not None:
        used += 1
        if active_change > 0:
            score += min(0.35, active_change / 10)
        elif active_change < 0:
            score -= min(0.35, abs(active_change) / 10)

    if tx_change is not None:
        used += 1
        if tx_change > 0:
            score += min(0.30, tx_change / 10)
        elif tx_change < 0:
            score -= min(0.30, abs(tx_change) / 10)

    if used == 0:
        return 0.0

    return _clip(score / used)


def _percentile_to_score(pct, fallback=0.25):
    if pct is None:
        return fallback

    return max(0.0, min(1.0, abs(float(pct) - 0.5) * 2))


def _clip(value: float, low: float = -1.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))
