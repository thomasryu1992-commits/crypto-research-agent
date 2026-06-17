def assign_signal_quality(score_row: dict, timeframe: str = "daily") -> dict:
    final_score = score_row.get("final_score", 0.0)
    bias = score_row.get("bias", "Neutral")
    market = score_row.get("market_structure_score", 0.0)
    deriv = score_row.get("derivatives_positioning_score", 0.0)
    cvd = score_row.get("cvd_flow_score", 0.0)
    volume = score_row.get("volume_score", 0.0)
    etf = score_row.get("etf_institutional_flow_score", 0.0)
    exchange = score_row.get("exchange_flow_score", 0.0)
    stable = score_row.get("stablecoin_liquidity_score", 0.0)
    valuation = score_row.get("valuation_cycle_score", 0.0)

    context = score_row.get("metric_context", {})
    rsi = context.get("rsi")
    oi_pct = context.get("oi_change_3_pctile") if timeframe == "daily" else context.get("oi_change_1_pctile")

    rsi_overheated = rsi is not None and rsi >= (72 if timeframe == "daily" else 76)
    oi_overheated = oi_pct is not None and oi_pct >= 0.88

    has_etf = abs(etf) > 0.001
    has_exchange = abs(exchange) > 0.001
    has_stable = abs(stable) > 0.001

    confirmations = 0
    warnings = 0
    reasons = []

    if market > 0.15:
        confirmations += 1
        reasons.append("market_structure_positive")
    elif market < -0.15:
        warnings += 1
        reasons.append("market_structure_negative")

    if cvd > 0:
        confirmations += 1
        reasons.append("cvd_positive")
    elif cvd < 0:
        warnings += 1
        reasons.append("cvd_negative")

    if deriv >= 0:
        confirmations += 1
        reasons.append("derivatives_not_negative")
    else:
        warnings += 1
        reasons.append("derivatives_negative")

    if has_etf:
        if etf > 0.15:
            confirmations += 1
            reasons.append("etf_inflow_support")
        elif etf < -0.15:
            warnings += 1
            reasons.append("etf_outflow_pressure")

    if has_exchange:
        if exchange > 0:
            confirmations += 1
            reasons.append("exchange_flow_constructive")
        elif exchange < 0:
            warnings += 1
            reasons.append("exchange_flow_bearish")

    if has_stable and stable > 0:
        confirmations += 1
        reasons.append("stablecoin_liquidity_positive")

    if valuation < -0.25:
        warnings += 1
        reasons.append("valuation_overheated")

    if rsi_overheated:
        warnings += 1
        reasons.append("rsi_overheated")

    if oi_overheated and final_score > 0:
        warnings += 1
        reasons.append("oi_overheated")

    # Grade logic
    if bias == "Bearish":
        grade = "F"
        label = "Bearish / Downside Pressure"

    elif bias == "Risk-Off":
        grade = "D"
        label = "Risk-Off / Upside Weakening"

    elif bias == "Bullish":
        if confirmations >= 4 and warnings <= 1 and not rsi_overheated and not oi_overheated:
            grade = "A"
            label = "High-Quality Upside Setup"
        elif confirmations >= 3 and warnings <= 2:
            grade = "B"
            label = "Confirmed but Moderate Upside Setup"
        else:
            grade = "C"
            label = "Weak Bullish Confirmation"

    elif bias == "Constructive":
        if confirmations >= 3 and warnings <= 1:
            grade = "B"
            label = "Early Upside Candidate"
        elif confirmations >= 2:
            grade = "C"
            label = "Constructive but Incomplete"
        else:
            grade = "N"
            label = "Neutral / Weak Edge"

    else:
        grade = "N"
        label = "Neutral / No Edge"

    return {
        "signal_quality": grade,
        "signal_quality_label": label,
        "confirmation_count": confirmations,
        "warning_count": warnings,
        "signal_reasons": "|".join(reasons),
    }
