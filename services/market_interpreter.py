def build_market_interpretation(market_data: dict) -> dict:
    snapshot = market_data.get("current_snapshot", {})
    delta = market_data.get("delta", {})
    market_context = market_data.get("market_context", {})
    candle_summary = market_data.get("candle_summary", {})

    price = snapshot.get("price")
    price_change_24h = snapshot.get("price_change_percent_24h")
    high_24h = snapshot.get("high_price_24h")
    low_24h = snapshot.get("low_price_24h")
    funding_rate = snapshot.get("funding_rate")
    open_interest = snapshot.get("open_interest")

    oi_change = delta.get("open_interest_change_since_last_snapshot")
    price_change_snapshot = delta.get("price_change_since_last_snapshot")
    volume_change = delta.get("volume_change_since_last_snapshot")

    funding_percent = _to_percent(funding_rate)

    return {
        "summary": {
            "symbol": snapshot.get("symbol"),
            "price": price,
            "price_change_24h": price_change_24h,
            "high_24h": high_24h,
            "low_24h": low_24h,
            "funding_rate_raw": funding_rate,
            "funding_rate_percent": funding_percent,
            "open_interest": open_interest,
            "open_interest_change_since_last_snapshot": oi_change,
            "price_change_since_last_snapshot": price_change_snapshot,
            "volume_change_since_last_snapshot": volume_change,
        },
        "bias": market_context.get("bias", "neutral"),
        "bias_text": _build_bias_text(
            market_context.get("bias"),
            price_change_24h,
            funding_percent,
            candle_summary,
        ),
        "structure_text": _build_structure_text(
            price,
            price_change_24h,
            high_24h,
            low_24h,
            candle_summary,
        ),
        "funding_text": _build_funding_text(funding_rate, funding_percent),
        "oi_text": _build_oi_text(open_interest, oi_change),
        "positioning_text": _build_positioning_text(
            market_context.get("positioning_structure")
        ),
        "long_text": _build_long_text(market_context),
        "short_text": _build_short_text(market_context),
        "risk_text": _build_risk_text(market_context),
        "plan_text": _build_plan_text(),
        "strict_language_rules": [
            "매수/매도 지시를 하지 않는다.",
            "롱/숏 진입을 고려한다는 표현을 쓰지 않는다.",
            "상방 시나리오와 하방 시나리오의 유효 조건만 설명한다.",
            "OI는 항상 시장 전체 OI라고 표현한다.",
            "현재는 추격 진입보다 확인 매매가 우선이라는 관점을 유지한다.",
        ],
    }


def _to_percent(value):
    try:
        if value is None:
            return None
        return float(value) * 100
    except (TypeError, ValueError):
        return None


def _fmt_num(value, decimals=4):
    try:
        if value is None:
            return "N/A"
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return "N/A"


def _fmt_pct(value, decimals=4, signed=True):
    try:
        if value is None:
            return "N/A"
        sign = "+" if signed and float(value) > 0 else ""
        return f"{sign}{float(value):.{decimals}f}%"
    except (TypeError, ValueError):
        return "N/A"


def _build_bias_text(bias, price_change_24h, funding_percent, candle_summary):
    trend = candle_summary.get("trend")
    bullish = candle_summary.get("bullish_candles")
    bearish = candle_summary.get("bearish_candles")
    candle_change = candle_summary.get("change_percent")

    if bias in ["mildly_bearish", "bearish_with_short_build_up", "neutral_to_bearish_with_long_trap_risk"]:
        base = "현재 시장 Bias는 약하방입니다."
    elif bias in ["mildly_bullish", "neutral_to_bullish", "bullish_but_overheated"]:
        base = "현재 시장 Bias는 약상방입니다."
    else:
        base = "현재 시장 Bias는 중립에 가깝습니다."

    detail = (
        f"24시간 가격 변화율은 {_fmt_pct(price_change_24h, 3)}이고, "
        f"최근 24개 1H 캔들은 {trend} 구조입니다. "
        f"상승 캔들 {bullish}개, 하락 캔들 {bearish}개이며, "
        f"최근 1H 묶음 기준 종가 변화율은 {_fmt_pct(candle_change, 3)}입니다. "
        f"Funding Rate는 {_fmt_pct(funding_percent, 6)} 수준입니다."
    )

    return f"{base} {detail}"


def _build_structure_text(price, price_change_24h, high_24h, low_24h, candle_summary):
    trend = candle_summary.get("trend")
    bullish = candle_summary.get("bullish_candles")
    bearish = candle_summary.get("bearish_candles")
    candle_change = candle_summary.get("change_percent")
    last_close = candle_summary.get("last_close")

    if trend == "downtrend":
        structure = "단기 구조는 하락 우위입니다."
    elif trend == "uptrend":
        structure = "단기 구조는 상승 우위입니다."
    elif trend == "range":
        structure = "단기 구조는 박스권에 가깝습니다."
    else:
        structure = "단기 구조는 명확하지 않습니다."

    return (
        f"현재 가격은 {_fmt_num(price, 2)}이며, 24시간 변화율은 {_fmt_pct(price_change_24h, 3)}입니다. "
        f"24시간 고가는 {_fmt_num(high_24h, 2)}, 저가는 {_fmt_num(low_24h, 2)}입니다. "
        f"최근 24개 1H 캔들 기준 마지막 종가는 {_fmt_num(last_close, 2)}이고, "
        f"해당 구간 종가 변화율은 {_fmt_pct(candle_change, 3)}입니다. "
        f"상승 캔들 {bullish}개, 하락 캔들 {bearish}개로 {structure} "
        f"현재는 추격 진입보다 확인 매매가 우선입니다."
    )


def _build_funding_text(funding_rate, funding_percent):
    if funding_rate is None:
        return "Funding Rate 데이터가 없어 포지셔닝 해석 신뢰도가 제한됩니다."

    if funding_rate > 0.0001:
        state = "양수이며 롱 쪽 비용 부담이 커지는 구간"
    elif funding_rate > 0:
        state = "양수지만 거의 중립에 가까운 구간"
    elif funding_rate < -0.0001:
        state = "음수이며 숏 쪽 비용 부담이 커지는 구간"
    elif funding_rate < 0:
        state = "음수지만 거의 중립에 가까운 구간"
    else:
        state = "중립에 가까운 구간"

    return f"Funding Rate는 {_fmt_pct(funding_percent, 6)}로, {state}입니다."


def _build_oi_text(open_interest, oi_change):
    if oi_change is None:
        return f"시장 전체 OI는 {_fmt_num(open_interest, 3)}입니다. 이전 스냅샷이 없어 변화율 판단은 제한됩니다."

    direction = "증가" if oi_change > 0 else "감소" if oi_change < 0 else "유지"
    return (
        f"시장 전체 OI는 {_fmt_num(open_interest, 3)}이며, "
        f"이전 스냅샷 대비 {_fmt_pct(oi_change, 3)} {direction}했습니다."
    )


def _build_positioning_text(positioning):
    readable = {
        "price_up_funding_positive_oi_up_long_overheat_risk": "가격 상승, 양수 Funding, 시장 전체 OI 증가 조합으로 롱 과열 가능성이 있습니다.",
        "price_up_funding_negative_oi_stable_or_up_short_pressure": "가격 상승, 음수 Funding, 시장 전체 OI 유지/증가 조합으로 숏 압박 가능성이 있습니다.",
        "price_up_oi_down_short_covering_possible": "가격 상승과 시장 전체 OI 감소 조합으로 포지션 축소성 상승 가능성이 있습니다.",
        "price_down_funding_positive_oi_up_long_trap_risk": "가격 하락, 양수 Funding, 시장 전체 OI 증가 조합으로 롱 트랩 리스크가 있습니다.",
        "price_down_funding_negative_oi_up_short_dominant": "가격 하락, 음수 Funding, 시장 전체 OI 증가 조합으로 숏 우위 흐름이 나타날 수 있습니다.",
        "price_down_oi_down_deleveraging": "가격 하락과 시장 전체 OI 감소 조합으로 디레버리징 가능성이 있습니다.",
        "mixed_or_range_positioning": "가격, Funding, 시장 전체 OI 조합이 혼재되어 방향성이 강하지 않습니다.",
        "insufficient_data": "포지셔닝 판단을 위한 데이터가 충분하지 않습니다.",
    }

    return readable.get(positioning, f"포지셔닝 구조는 {positioning}입니다.")


def _build_long_text(market_context):
    long_setup = market_context.get("long_setup", {})
    thesis = long_setup.get("thesis", "상방 시나리오는 확인 조건이 필요합니다.")
    return (
        f"{thesis} 상방 시나리오는 직전 고점 또는 단기 저항 돌파, "
        f"1H 종가의 돌파 구간 위 마감, 시장 전체 OI 유지 또는 증가, "
        f"Funding Rate 중립 유지, 가격 상승 시 거래량 동반이 확인될 때 강화됩니다."
    )


def _build_short_text(market_context):
    short_setup = market_context.get("short_setup", {})
    thesis = short_setup.get("thesis", "하방 시나리오는 확인 조건이 필요합니다.")
    return (
        f"{thesis} 하방 시나리오는 단기 지지 구간 또는 현재 가격대 하단 이탈, "
        f"1H 종가의 이탈 구간 아래 마감, 반등 시 이전 지지 구간 회복 실패, "
        f"하락 중 시장 전체 OI 유지 또는 증가, 반등 시 거래량 부족이 확인될 때 강화됩니다."
    )


def _build_risk_text(market_context):
    risk_level = market_context.get("risk_level", "Medium")
    return (
        f"현재 리스크 등급은 {risk_level}입니다. "
        f"가장 주의해야 할 행동은 확인 없는 추격 진입, 지지/저항 근처에서의 늦은 대응, "
        f"시장 전체 OI가 급변하는 구간에서의 과도한 레버리지 사용입니다."
    )


def _build_plan_text():
    return (
        "상방 대응은 단기 저항 회복과 1H 종가 유지가 확인될 때만 유효합니다. "
        "하방 대응은 단기 지지 이탈과 이탈 구간 아래 1H 마감, 이후 반등 실패가 확인될 때만 유효합니다. "
        "가격이 지지와 저항 사이에 머무르고 시장 전체 OI와 Funding이 뚜렷한 방향성을 보이지 않으면 대기가 우선입니다."
    )
