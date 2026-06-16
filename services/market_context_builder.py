def build_market_context(snapshot: dict, delta: dict, previous_snapshot: dict | None) -> dict:
    price_change_24h = snapshot.get("price_change_percent_24h")
    funding = snapshot.get("funding_rate")
    oi_change = delta.get("open_interest_change_since_last_snapshot")
    price_change_snapshot = delta.get("price_change_since_last_snapshot")
    volume_change = delta.get("volume_change_since_last_snapshot")
    candle_summary = snapshot.get("candle_summary", {})
    candle_trend = candle_summary.get("trend")

    bias = _classify_bias(price_change_24h, funding, oi_change, candle_trend)
    positioning = _classify_positioning(price_change_24h, funding, oi_change, price_change_snapshot)
    risk_level = _classify_risk(price_change_24h, funding, oi_change, candle_trend)
    chasing_allowed = _is_chasing_allowed(bias, positioning, risk_level)

    long_setup = _build_long_setup(positioning, bias, candle_trend)
    short_setup = _build_short_setup(positioning, bias, candle_trend)

    return {
        "bias": bias,
        "positioning_structure": positioning,
        "risk_level": risk_level,
        "chasing_allowed": chasing_allowed,
        "recommended_mode": "confirmation_required" if not chasing_allowed else "momentum_confirmation_required",
        "long_setup": long_setup,
        "short_setup": short_setup,
        "invalidation_rules": _build_invalidation_rules(),
        "data_quality": _assess_data_quality(delta, candle_summary),
        "notes_for_llm": _build_notes_for_llm(chasing_allowed, positioning),
        "raw_inputs_used": {
            "price_change_percent_24h": price_change_24h,
            "funding_rate": funding,
            "open_interest_change_since_last_snapshot": oi_change,
            "price_change_since_last_snapshot": price_change_snapshot,
            "volume_change_since_last_snapshot": volume_change,
            "candle_trend": candle_trend,
        },
    }


def _classify_bias(price_change_24h, funding, oi_change, candle_trend) -> str:
    if price_change_24h is None or funding is None:
        return "neutral"

    if price_change_24h > 1 and candle_trend == "uptrend":
        if funding < 0:
            return "neutral_to_bullish"
        if funding > 0 and oi_change is not None and oi_change > 1:
            return "bullish_but_overheated"
        return "mildly_bullish"

    if price_change_24h < -1 and candle_trend == "downtrend":
        if funding > 0:
            return "neutral_to_bearish_with_long_trap_risk"
        if funding < 0 and oi_change is not None and oi_change > 1:
            return "bearish_with_short_build_up"
        return "mildly_bearish"

    return "neutral"


def _classify_positioning(price_change_24h, funding, oi_change, price_change_snapshot) -> str:
    if price_change_24h is None or funding is None:
        return "insufficient_data"

    oi_up = oi_change is not None and oi_change > 0.2
    oi_down = oi_change is not None and oi_change < -0.2

    if price_change_24h > 0 and funding > 0 and oi_up:
        return "price_up_funding_positive_oi_up_long_overheat_risk"

    if price_change_24h > 0 and funding < 0 and (oi_up or oi_change is None):
        return "price_up_funding_negative_oi_stable_or_up_short_pressure"

    if price_change_24h > 0 and oi_down:
        return "price_up_oi_down_short_covering_possible"

    if price_change_24h < 0 and funding > 0 and oi_up:
        return "price_down_funding_positive_oi_up_long_trap_risk"

    if price_change_24h < 0 and funding < 0 and oi_up:
        return "price_down_funding_negative_oi_up_short_dominant"

    if price_change_24h < 0 and oi_down:
        return "price_down_oi_down_deleveraging"

    return "mixed_or_range_positioning"


def _classify_risk(price_change_24h, funding, oi_change, candle_trend) -> str:
    if price_change_24h is None or funding is None:
        return "medium"

    abs_price_change = abs(price_change_24h)
    abs_funding = abs(funding)
    abs_oi_change = abs(oi_change) if oi_change is not None else 0

    if abs_price_change >= 3 or abs_oi_change >= 5:
        return "high"

    if abs_price_change >= 1 or abs_funding > 0.0001 or abs_oi_change >= 1:
        return "medium"

    return "low"


def _is_chasing_allowed(bias: str, positioning: str, risk_level: str) -> bool:
    # For this research bot, chasing is almost always discouraged unless momentum is very clear.
    # Even then the report should require confirmation, not direct entry.
    if risk_level == "high":
        return False

    if bias in ["bullish_but_overheated", "neutral_to_bullish"] and "short_pressure" in positioning:
        return False

    if bias in ["mildly_bullish", "mildly_bearish"]:
        return False

    return False


def _build_long_setup(positioning: str, bias: str, candle_trend: str | None) -> dict:
    if "short_pressure" in positioning:
        setup_type = "breakout_confirmation_long"
        thesis = "가격 상승, 음수 Funding, OI 유지/증가 조합은 숏 포지션 압박 구조일 수 있습니다."
    elif "long_overheat" in positioning:
        setup_type = "long_allowed_only_after_retest"
        thesis = "롱 유입은 강하지만 과열 리스크가 있어 돌파 추격보다 리테스트 확인이 필요합니다."
    else:
        setup_type = "conditional_long_only"
        thesis = "롱 시나리오는 직전 고점 돌파와 1H 종가 유지가 확인될 때만 강화됩니다."

    return {
        "setup_type": setup_type,
        "thesis": thesis,
        "valid_conditions": [
            "직전 고점 또는 단기 저항 돌파",
            "1H 종가가 돌파 구간 위에서 마감",
            "OI가 급감하지 않고 유지 또는 증가",
            "Funding Rate가 음수 또는 중립 수준 유지",
            "가격 상승 시 거래량 동반",
        ],
        "do_not_say": [
            "추격 진입이 유리하다",
            "즉시 롱 진입",
            "무조건 상승",
        ],
    }


def _build_short_setup(positioning: str, bias: str, candle_trend: str | None) -> dict:
    if "long_trap" in positioning:
        setup_type = "support_breakdown_short"
        thesis = "가격 하락, 양수 Funding, OI 증가 조합은 롱 포지션이 갇히는 구조일 수 있습니다."
    elif "short_dominant" in positioning:
        setup_type = "trend_continuation_short"
        thesis = "가격 하락, 음수 Funding, OI 증가 조합은 신규 숏 유입 또는 숏 우위 추세일 수 있습니다."
    else:
        setup_type = "conditional_short_only"
        thesis = "숏 시나리오는 단기 지지 이탈과 회복 실패가 확인될 때만 강화됩니다."

    return {
        "setup_type": setup_type,
        "thesis": thesis,
        "valid_conditions": [
            "현재 상승 흐름 유지 실패",
            "단기 지지 구간 또는 현재 가격대 하단 이탈",
            "1H 종가가 이탈 구간 아래에서 마감",
            "이탈 후 반등 시 이전 지지 구간 회복 실패",
            "하락 중 OI 유지 또는 증가",
            "반등 시 거래량 부족",
        ],
        "do_not_say": [
            "숏 포지션을 청산",
            "숏 커버링 필요",
            "즉시 숏 진입",
            "무조건 하락",
        ],
    }


def _build_invalidation_rules() -> dict:
    return {
        "long_invalidation": [
            "돌파 후 1H 종가 유지 실패",
            "단기 지지 구간 이탈",
            "가격 하락과 함께 OI 증가",
            "OI 급감과 가격 하락이 동시에 발생",
        ],
        "short_invalidation": [
            "직전 고점 또는 단기 저항 강한 돌파",
            "1H 종가가 저항 위에서 유지",
            "OI 유지 또는 증가와 함께 가격 상승",
            "Funding이 음수에서 중립으로 회복되며 가격 상승 지속",
        ],
    }


def _assess_data_quality(delta: dict, candle_summary: dict) -> dict:
    has_snapshot = delta.get("has_previous_snapshot", False)
    has_candles = candle_summary.get("available", False)

    if has_snapshot and has_candles:
        level = "good"
    elif has_snapshot or has_candles:
        level = "partial"
    else:
        level = "limited"

    return {
        "level": level,
        "has_previous_snapshot": has_snapshot,
        "has_candle_data": has_candles,
        "message": "이전 스냅샷과 캔들 데이터가 모두 있으면 변화율 기반 해석의 신뢰도가 높아집니다.",
    }


def _build_notes_for_llm(chasing_allowed: bool, positioning: str) -> list[str]:
    notes = []

    if not chasing_allowed:
        notes.append("절대로 '추격 진입이 유리하다'고 쓰지 마라. 현재는 확인 매매 또는 조건부 대응 구간으로 표현해라.")

    if "short_pressure" in positioning:
        notes.append("숏 압박 구조는 가능하지만, Funding 음수만으로 숏 스퀴즈를 단정하지 마라. 저항 돌파와 1H 종가 유지가 필요하다고 써라.")

    if "long_overheat" in positioning:
        notes.append("롱 과열 가능성을 언급하고, 돌파 추격보다 리테스트 또는 OI/Funding 안정화 확인이 필요하다고 써라.")

    if "long_trap" in positioning:
        notes.append("롱 포지션이 갇힐 수 있는 구조를 설명하고, 지지선 이탈 시 하방 변동성이 커질 수 있다고 써라.")

    notes.append("Short Scenario 섹션에서는 '숏 청산', '숏 커버링', '포지션 종료'라는 표현을 쓰지 마라.")
    notes.append("Trading Plan에서는 매수/매도 명령이 아니라 관찰 조건만 제시해라.")

    return notes
