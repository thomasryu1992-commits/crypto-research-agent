from core.calibration_loader import get_timeframe_calibration


def classify_scenario(score_row: dict, timeframe: str = "daily", calibration: dict | None = None) -> dict:
    if timeframe == "weekly":
        return _classify_weekly(score_row, calibration)
    return _classify_daily(score_row, calibration)


def _classify_daily(score_row: dict, calibration: dict | None = None) -> dict:
    c = get_timeframe_calibration(calibration, "daily")

    final_score = score_row.get("final_score", 0.0)
    market = score_row.get("market_structure_score", 0.0)
    deriv = score_row.get("derivatives_positioning_score", 0.0)
    cvd = score_row.get("cvd_flow_score", 0.0)
    etf = score_row.get("etf_institutional_flow_score", 0.0)
    exchange = score_row.get("exchange_flow_score", 0.0)
    stable = score_row.get("stablecoin_liquidity_score", 0.0)

    context = score_row.get("metric_context", {})
    rsi = context.get("rsi")
    oi_pct = context.get("oi_change_3_pctile")

    rsi_overheated = rsi is not None and rsi >= 72
    oi_overheated = oi_pct is not None and oi_pct >= 0.88

    has_etf = abs(etf) > 0.001
    has_exchange = abs(exchange) > 0.001
    has_stable = abs(stable) > 0.001

    # V3.6: Bullish is stricter.
    bullish_confirmed = (
        final_score >= c["bullish_threshold"]
        and market > c["market_confirm_threshold"]
        and cvd > 0
        and deriv >= -0.10
        and etf >= 0
        and not rsi_overheated
        and not oi_overheated
    )

    constructive_confirmed = (
        final_score >= c["constructive_threshold"]
        and market > 0
        and (cvd >= 0 or etf > 0)
        and not (rsi is not None and rsi >= 78)
    )

    bearish_confirmed = (
        final_score <= c["bearish_threshold"]
        and market < c["market_bearish_confirm_threshold"]
        and (deriv < 0 or cvd < 0 or exchange < 0)
    )

    if bullish_confirmed:
        bias = "Bullish"
    elif bearish_confirmed:
        bias = "Bearish"
    elif final_score <= c["risk_off_threshold"]:
        bias = "Risk-Off"
    elif constructive_confirmed:
        bias = "Constructive"
    else:
        bias = "Neutral"

    scenario = "Neutral / Wait"
    confidence = "Low"

    if has_etf and has_exchange and etf > 0.35 and exchange > 0.10 and cvd >= 0:
        scenario = "Institutional Accumulation"
        confidence = "Medium"
        if bullish_confirmed:
            bias = "Bullish"
        elif constructive_confirmed:
            bias = "Constructive"

    elif has_etf and etf > 0.35 and market <= 0 and exchange < 0:
        scenario = "ETF Demand Absorption"
        confidence = "Medium"
        bias = "Risk-Off"

    elif has_etf and has_exchange and etf < -0.35 and exchange < -0.10:
        scenario = "Institutional Distribution"
        confidence = "Medium"
        bias = "Bearish" if final_score <= c["bearish_threshold"] else "Risk-Off"

    elif bias == "Bullish":
        scenario = "High-Quality Upside Momentum"
        confidence = "Medium"

    elif bias == "Constructive":
        scenario = "Early Upside Candidate"
        confidence = "Low"

    elif bias == "Bearish":
        scenario = "Confirmed Downside Pressure"
        confidence = "Medium"

    elif bias == "Risk-Off":
        scenario = "Risk-Off / Upside Weakening"
        confidence = "Low"

    if has_stable and stable > 0.35 and bias in ["Bullish", "Constructive"]:
        confidence = _raise_confidence(confidence)

    if abs(final_score) >= 0.65 and bias in ["Bullish", "Bearish"]:
        confidence = "High"

    return {"bias": bias, "scenario": scenario, "confidence": confidence}


def _classify_weekly(score_row: dict, calibration: dict | None = None) -> dict:
    c = get_timeframe_calibration(calibration, "weekly")

    final_score = score_row.get("final_score", 0.0)
    market = score_row.get("market_structure_score", 0.0)
    deriv = score_row.get("derivatives_positioning_score", 0.0)
    cvd = score_row.get("cvd_flow_score", 0.0)
    etf = score_row.get("etf_institutional_flow_score", 0.0)
    exchange = score_row.get("exchange_flow_score", 0.0)
    stable = score_row.get("stablecoin_liquidity_score", 0.0)
    valuation = score_row.get("valuation_cycle_score", 0.0)

    context = score_row.get("metric_context", {})
    rsi = context.get("rsi")
    oi_pct = context.get("oi_change_1_pctile")

    rsi_overheated = rsi is not None and rsi >= 78
    oi_overheated = oi_pct is not None and oi_pct >= 0.90

    has_etf = abs(etf) > 0.001
    has_exchange = abs(exchange) > 0.001

    bullish_confirmed = (
        final_score >= c["bullish_threshold"]
        and market > c["market_confirm_threshold"]
        and cvd > 0
        and deriv >= -0.10
        and not rsi_overheated
        and not oi_overheated
    )

    constructive_confirmed = (
        final_score >= c["constructive_threshold"]
        and market > 0
        and (cvd >= 0 or etf > 0)
    )

    bearish_confirmed = (
        final_score <= c["bearish_threshold"]
        and market < c["market_bearish_confirm_threshold"]
        and (deriv < 0 or cvd < 0 or exchange < 0)
    )

    if bullish_confirmed:
        bias = "Bullish"
    elif bearish_confirmed:
        bias = "Bearish"
    elif final_score <= c["risk_off_threshold"]:
        bias = "Risk-Off"
    elif constructive_confirmed:
        bias = "Constructive"
    else:
        bias = "Neutral"

    scenario = "Neutral / Wait"
    confidence = "Low"

    if has_etf and has_exchange and etf > 0.30 and exchange > 0 and cvd >= 0:
        scenario = "Institutional Accumulation"
        confidence = "Medium"
        if bullish_confirmed:
            bias = "Bullish"
        elif constructive_confirmed:
            bias = "Constructive"

    elif has_etf and has_exchange and etf < -0.30 and exchange < 0:
        scenario = "Institutional Distribution"
        confidence = "Medium"
        bias = "Bearish" if final_score <= c["bearish_threshold"] else "Risk-Off"

    elif bias == "Bullish":
        scenario = "Momentum Continuation"
        confidence = "Medium"

    elif bias == "Constructive":
        scenario = "Constructive Trend"
        confidence = "Low"

    elif bias == "Bearish":
        scenario = "Bearish Regime"
        confidence = "Medium"

    elif bias == "Risk-Off":
        scenario = "Risk-Off / Upside Weakening"
        confidence = "Low"

    if stable > 0.30 and valuation >= -0.10 and bias in ["Bullish", "Constructive"]:
        confidence = _raise_confidence(confidence)

    if final_score >= 0.60 and scenario in ["Momentum Continuation", "Institutional Accumulation"]:
        confidence = "High"

    if final_score <= -0.75 and scenario in ["Bearish Regime", "Institutional Distribution"]:
        confidence = "High"

    return {"bias": bias, "scenario": scenario, "confidence": confidence}


def _raise_confidence(confidence: str) -> str:
    if confidence == "Low":
        return "Medium"
    if confidence == "Medium":
        return "High"
    return confidence
