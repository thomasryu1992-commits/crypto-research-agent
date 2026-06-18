def to_float(value, default=0.0):
    try:
        if value == "" or value is None:
            return default
        return float(value)
    except Exception:
        return default


def get_research_direction(latest_row):
    """
    기존 Crypto Research Agent의 score/scenario 결과에서 방향성을 추출한다.
    repo마다 key 이름이 다를 수 있으므로 여러 후보를 확인한다.
    """
    if latest_row is None:
        return "neutral"

    candidates = [
        latest_row.get("scenario"),
        latest_row.get("market_scenario"),
        latest_row.get("label"),
        latest_row.get("signal"),
        latest_row.get("direction"),
    ]

    text = " ".join([str(item).lower() for item in candidates if item is not None])

    if "strong bullish" in text or "bullish" in text or "long" in text:
        return "bullish"

    if "strong bearish" in text or "bearish" in text or "short" in text:
        return "bearish"

    return "neutral"


def get_trading_context_direction(trading_context):
    """
    Trading Bot context의 market_state와 risk_flags를 기반으로 실시간 방향성을 추정한다.
    """
    if not trading_context:
        return "neutral"

    market_state = trading_context.get("market_state", {})
    market_label = str(market_state.get("market_state", "")).lower()
    market_score = to_float(market_state.get("market_score"))

    risk_flags = trading_context.get("risk_flags", [])

    bearish_flags = {
        "long_crowding",
        "extreme_long_crowding",
        "funding_overheated",
        "trapped_longs",
        "downside_leverage_risk",
        "long_squeeze_risk",
        "crowded_long_with_leverage",
        "bearish_score",
        "strong_bearish_score",
    }

    bullish_flags = {
        "short_crowding",
        "extreme_short_crowding",
        "healthy_positive_funding",
        "negative_funding_extreme",
        "trend_participation",
        "oi_expansion",
        "bullish_score",
        "strong_bullish_score",
    }

    bearish_count = len([flag for flag in risk_flags if flag in bearish_flags])
    bullish_count = len([flag for flag in risk_flags if flag in bullish_flags])

    if "strong bullish" in market_label or market_score >= 1.2:
        return "bullish"

    if "bullish" in market_label or market_score >= 0.5:
        if bearish_count > bullish_count:
            return "bullish_with_risk"
        return "bullish"

    if "strong bearish" in market_label or market_score <= -1.2:
        return "bearish"

    if "bearish" in market_label or market_score <= -0.5:
        return "bearish"

    if bearish_count > bullish_count:
        return "caution_bearish"

    if bullish_count > bearish_count:
        return "caution_bullish"

    return "neutral"


def classify_overlay_status(research_direction, trading_direction):
    """
    기존 Research Agent 방향성과 Trading Bot 실시간 방향성을 비교한다.
    """
    if trading_direction in ["neutral"]:
        return "Neutral Overlay"

    if research_direction == "bullish" and trading_direction == "bullish":
        return "Confirmed Bullish"

    if research_direction == "bearish" and trading_direction == "bearish":
        return "Confirmed Bearish"

    if research_direction == "bullish" and trading_direction == "bullish_with_risk":
        return "Bullish but Risk Elevated"

    if research_direction == "bullish" and trading_direction in ["caution_bearish", "bearish"]:
        return "Bullish Signal Conflict"

    if research_direction == "bearish" and trading_direction in ["caution_bullish", "bullish"]:
        return "Bearish Signal Conflict"

    if research_direction == "neutral" and trading_direction in ["caution_bearish", "bearish"]:
        return "Neutral with Bearish Risk"

    if research_direction == "neutral" and trading_direction in ["caution_bullish", "bullish"]:
        return "Neutral with Bullish Bias"

    return "Mixed Overlay"


def build_overlay_summary(research_direction, trading_direction, overlay_status):
    if overlay_status == "Confirmed Bullish":
        return (
            "기존 Research Agent의 방향성과 Trading Bot의 실시간 파생 데이터가 모두 상승 쪽을 지지합니다. "
            "다만 Funding과 Long/Short Ratio 과열 여부는 계속 확인해야 합니다."
        )

    if overlay_status == "Bullish but Risk Elevated":
        return (
            "기존 방향성은 상승 쪽에 가깝지만, 실시간 파생 데이터에서 포지션 과밀 리스크가 감지됩니다. "
            "상승 추세는 유지될 수 있으나 신규 진입은 지지선과 청산 리스크를 함께 확인해야 합니다."
        )

    if overlay_status == "Confirmed Bearish":
        return (
            "기존 Research Agent의 방향성과 Trading Bot의 실시간 파생 데이터가 모두 하방 리스크를 가리킵니다. "
            "가격이 지지선을 회복하지 못하면 추가 하락 가능성이 높아질 수 있습니다."
        )

    if overlay_status == "Bullish Signal Conflict":
        return (
            "기존 Research Agent는 상승 또는 회복 가능성을 보지만, 실시간 파생 데이터는 하방 리스크를 경고하고 있습니다. "
            "이 경우 상승 시그널의 신뢰도를 낮추고, 지지선 이탈 여부를 우선 확인해야 합니다."
        )

    if overlay_status == "Bearish Signal Conflict":
        return (
            "기존 Research Agent는 하방 리스크를 보지만, 실시간 파생 데이터는 반등 또는 숏 포지션 과밀 가능성을 보여줍니다. "
            "이 경우 하락 추세 지속보다 단기 반등 가능성도 함께 봐야 합니다."
        )

    if overlay_status == "Neutral with Bearish Risk":
        return (
            "기존 방향성은 중립에 가깝지만 실시간 파생 데이터는 하방 리스크를 보여줍니다. "
            "특히 롱 포지션 쏠림, OI 증가, 청산 증가가 동시에 나타나는지 확인해야 합니다."
        )

    if overlay_status == "Neutral with Bullish Bias":
        return (
            "기존 방향성은 중립에 가깝지만 실시간 파생 데이터는 완만한 상승 가능성을 보여줍니다. "
            "가격 상승과 OI 증가가 함께 이어지는지 확인해야 합니다."
        )

    return (
        "기존 리서치 시그널과 실시간 파생 데이터가 명확하게 한 방향으로 정렬되어 있지는 않습니다. "
        "다음 업데이트에서는 가격, OI, Funding, Long/Short Ratio 변화를 함께 확인해야 합니다."
    )


def build_overlay_scenarios(trading_context, overlay_status):
    key_metrics = trading_context.get("key_metrics", {}) if trading_context else {}
    risk_flags = trading_context.get("risk_flags", []) if trading_context else []

    long_short_ratio = to_float(key_metrics.get("long_short_ratio"))
    funding_rate = to_float(key_metrics.get("funding_rate"))
    oi_change_4h = to_float(key_metrics.get("oi_change_4h"))
    liquidation_24h = to_float(key_metrics.get("liquidation_24h"))

    base = (
        "Base Scenario: 현재 시장은 기존 리서치 점수와 실시간 파생 데이터의 정렬 여부를 함께 봐야 합니다. "
        "단일 지표보다 가격 변화, OI 변화, Funding, Long/Short Ratio 조합이 중요합니다."
    )

    bullish = (
        "Bullish Scenario: 가격이 주요 저항선을 돌파하고 OI가 함께 증가하면서 Funding이 과열되지 않는다면 "
        "상승 추세 지속 가능성이 강화됩니다."
    )

    bearish = (
        "Bearish Scenario: 가격이 주요 지지선을 이탈하고 OI가 유지되거나 증가한다면 "
        "롱 포지션이 물리는 구조가 될 수 있습니다."
    )

    if long_short_ratio >= 1.3:
        base = (
            "Base Scenario: Long/Short Ratio가 높은 상태이므로 시장은 롱 포지션 쏠림 구간입니다. "
            "가격이 지지선 위에 머물면 상승 흐름은 유지될 수 있지만, 지지선 이탈 시 롱 청산 압력이 커질 수 있습니다."
        )

    if "trend_participation" in risk_flags and funding_rate < 0.0005:
        bullish = (
            "Bullish Scenario: 가격 상승과 OI 증가가 함께 나타나 신규 포지션 참여가 확인됩니다. "
            "Funding이 아직 과열되지 않았다면 상승 추세 지속 가능성이 있습니다."
        )

    if "crowded_long_with_leverage" in risk_flags or "long_squeeze_risk" in risk_flags:
        bearish = (
            "Bearish Scenario: 롱 포지션 쏠림과 레버리지 증가가 동시에 나타나고 있습니다. "
            "가격이 주요 지지선을 잃으면 롱 청산이 연쇄적으로 발생할 수 있습니다."
        )

    if liquidation_24h >= 300_000_000:
        bearish += (
            " 또한 24시간 청산 규모가 매우 크기 때문에 단기 변동성 확대 가능성이 높습니다."
        )

    return {
        "base_scenario": base,
        "bullish_scenario": bullish,
        "bearish_scenario": bearish,
    }


def build_watch_conditions(trading_context):
    key_metrics = trading_context.get("key_metrics", {}) if trading_context else {}

    return [
        "가격 상승 + OI 증가 여부",
        "가격 하락 + OI 증가 시 trapped longs 가능성",
        "Funding Rate 과열 여부",
        "Long/Short Ratio 추가 상승 여부",
        "liquidation_24h 증가 또는 급감 여부",
        "기존 Research Agent 시그널과 Trading Bot context의 정렬 여부",
    ]


def build_context_overlay(latest_row, trading_context):
    research_direction = get_research_direction(latest_row)
    trading_direction = get_trading_context_direction(trading_context)
    overlay_status = classify_overlay_status(research_direction, trading_direction)

    overlay_summary = build_overlay_summary(
        research_direction,
        trading_direction,
        overlay_status,
    )

    scenarios = build_overlay_scenarios(trading_context, overlay_status)
    watch_conditions = build_watch_conditions(trading_context)

    return {
        "research_direction": research_direction,
        "trading_context_direction": trading_direction,
        "overlay_status": overlay_status,
        "overlay_summary": overlay_summary,
        "base_scenario": scenarios.get("base_scenario"),
        "bullish_scenario": scenarios.get("bullish_scenario"),
        "bearish_scenario": scenarios.get("bearish_scenario"),
        "watch_conditions": watch_conditions,
    }