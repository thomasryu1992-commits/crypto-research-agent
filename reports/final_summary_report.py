def get_overlay_status(overlay):
    if not overlay:
        return "Unknown"

    return overlay.get("overlay_status", "Unknown")


def get_market_score(context):
    if not context:
        return None

    market_state = context.get("market_state", {})
    return market_state.get("market_score")


def get_market_state(context):
    if not context:
        return "Unknown"

    market_state = context.get("market_state", {})
    return market_state.get("market_state", "Unknown")


def get_risk_flags(context):
    if not context:
        return []

    flags = context.get("risk_flags", [])

    if isinstance(flags, list):
        return flags

    return []


def classify_conviction(overlay_status, risk_flags):
    """
    Research conclusion의 신뢰도 레벨을 분류한다.
    """
    high_confidence_status = {
        "Confirmed Bullish",
        "Confirmed Bearish",
    }

    conflict_status = {
        "Bullish Signal Conflict",
        "Bearish Signal Conflict",
        "Mixed Overlay",
    }

    high_risk_flags = {
        "extreme_long_crowding",
        "extreme_short_crowding",
        "funding_overheated",
        "liquidation_spike",
        "long_squeeze_risk",
        "crowded_long_with_leverage",
        "trapped_longs",
    }

    if overlay_status in high_confidence_status:
        if any(flag in risk_flags for flag in high_risk_flags):
            return "Medium"
        return "High"

    if overlay_status in conflict_status:
        return "Low"

    if any(flag in risk_flags for flag in high_risk_flags):
        return "Medium-Low"

    return "Medium"


def identify_main_risk(risk_flags):
    """
    risk_flags를 기반으로 가장 중요한 리스크를 요약한다.
    """
    if not risk_flags:
        return "뚜렷한 실시간 파생 리스크는 감지되지 않았습니다."

    if "crowded_long_with_leverage" in risk_flags:
        return "롱 포지션 쏠림과 레버리지 증가가 동시에 나타나 지지선 이탈 시 롱 청산 압력이 커질 수 있습니다."

    if "long_squeeze_risk" in risk_flags:
        return "롱 포지션 쏠림 상태에서 가격이 약해질 경우 롱 청산 압력이 확대될 수 있습니다."

    if "funding_overheated" in risk_flags:
        return "Funding Rate 과열로 인해 상승 포지션이 과밀해져 단기 되돌림 리스크가 커질 수 있습니다."

    if "trapped_longs" in risk_flags:
        return "가격 하락 중 OI 증가가 나타나 롱 포지션이 물리는 구조일 수 있습니다."

    if "liquidation_spike" in risk_flags:
        return "24시간 청산 규모가 크게 증가해 단기 변동성이 확대될 수 있습니다."

    if "short_covering_rebound" in risk_flags:
        return "가격 반등이 신규 매수세가 아니라 숏 커버링일 가능성이 있어 추세 지속 신뢰도가 낮을 수 있습니다."

    if "position_flush" in risk_flags or "deleveraging" in risk_flags:
        return "포지션 정리 구간으로, 방향성보다는 변동성 축소 또는 재진입 대기 흐름일 수 있습니다."

    return "파생 포지션 구조 변화가 감지되며, 가격과 OI의 다음 변화가 중요합니다."


def build_overall_view(overlay, context):
    overlay_status = get_overlay_status(overlay)
    market_state = get_market_state(context)
    market_score = get_market_score(context)
    risk_flags = get_risk_flags(context)

    if overlay_status == "Confirmed Bullish":
        return (
            f"현재 BTC는 기존 리서치 모델과 실시간 파생 데이터가 모두 상승 방향을 지지합니다. "
            f"Trading Bot 기준 market_state는 {market_state}, market_score는 {market_score}입니다. "
            "다만 Funding과 Long/Short Ratio가 과열되는지 계속 확인해야 합니다."
        )

    if overlay_status == "Bullish but Risk Elevated":
        return (
            f"현재 BTC는 상승 구조를 유지하고 있지만, 실시간 파생 데이터에서 리스크가 높아진 상태입니다. "
            f"market_state는 {market_state}, market_score는 {market_score}이며, "
            "롱 포지션 쏠림이나 레버리지 증가가 동반될 경우 신규 진입 신뢰도는 낮아질 수 있습니다."
        )

    if overlay_status == "Confirmed Bearish":
        return (
            f"현재 BTC는 기존 리서치 모델과 실시간 파생 데이터가 모두 하방 리스크를 가리키고 있습니다. "
            f"market_state는 {market_state}, market_score는 {market_score}입니다. "
            "지지선 회복 실패와 OI 증가가 이어질 경우 추가 하락 가능성을 우선적으로 봐야 합니다."
        )

    if overlay_status == "Bullish Signal Conflict":
        return (
            "기존 Research Agent는 상승 또는 회복 가능성을 보지만, 실시간 파생 데이터는 하방 리스크를 경고하고 있습니다. "
            "이 경우 기존 상승 시나리오의 신뢰도를 낮추고, 지지선 이탈 여부와 청산 데이터를 우선 확인해야 합니다."
        )

    if overlay_status == "Bearish Signal Conflict":
        return (
            "기존 Research Agent는 하방 리스크를 보지만, 실시간 파생 데이터는 반등 가능성을 일부 보여주고 있습니다. "
            "이 경우 공격적인 하락 추종보다는 숏 커버링 또는 포지션 리셋 가능성도 함께 고려해야 합니다."
        )

    if overlay_status == "Neutral with Bearish Risk":
        return (
            "기존 리서치 방향성은 중립에 가깝지만, 실시간 파생 데이터는 하방 리스크를 보여주고 있습니다. "
            "특히 롱 포지션 쏠림, OI 증가, liquidation_24h 증가 여부가 핵심 확인 포인트입니다."
        )

    if overlay_status == "Neutral with Bullish Bias":
        return (
            "기존 리서치 방향성은 중립에 가깝지만, 실시간 파생 데이터는 완만한 상승 가능성을 보여주고 있습니다. "
            "가격 상승과 OI 증가가 함께 유지되는지 확인해야 합니다."
        )

    if risk_flags:
        return (
            "현재 BTC는 명확한 단일 방향성보다는 파생 포지션 구조를 중심으로 해석해야 하는 구간입니다. "
            "기존 리서치 시그널과 실시간 데이터의 정렬 여부를 다음 업데이트에서 계속 확인해야 합니다."
        )

    return (
        "현재 BTC는 뚜렷한 방향성보다는 중립적 흐름에 가깝습니다. "
        "가격 변화, OI 변화, Funding, Long/Short Ratio 조합을 추가 확인해야 합니다."
    )


def suggest_best_action(overlay_status, conviction, risk_flags):
    """
    리서치 관점의 행동 가이드.
    직접 매수/매도 지시가 아니라 관찰 우선순위를 정리한다.
    """
    if overlay_status == "Confirmed Bullish" and conviction == "High":
        return (
            "상승 시나리오 우위 구간입니다. 다만 진입 판단은 가격이 주요 지지선 위에서 유지되고 "
            "Funding과 Long/Short Ratio가 과열되지 않는지 확인한 뒤 판단하는 것이 좋습니다."
        )

    if overlay_status == "Bullish but Risk Elevated":
        return (
            "상승 방향성은 유지되지만 파생 리스크가 높아진 구간입니다. "
            "신규 진입보다는 지지선 유지, OI 증가의 질, Long/Short Ratio 추가 과열 여부를 먼저 확인해야 합니다."
        )

    if overlay_status == "Confirmed Bearish":
        return (
            "하방 리스크 우위 구간입니다. 반등 추격보다는 지지선 회복 여부와 OI 감소 여부를 확인하는 것이 중요합니다."
        )

    if "long_crowding" in risk_flags or "crowded_long_with_leverage" in risk_flags:
        return (
            "롱 포지션 쏠림이 존재하므로 가격이 지지선을 잃는지 우선 확인해야 합니다. "
            "지지선 이탈 전까지는 추세 지속 가능성과 청산 리스크가 공존합니다."
        )

    if "short_covering_rebound" in risk_flags:
        return (
            "반등이 숏 커버링일 가능성이 있으므로 추세 지속 확인 전까지는 보수적으로 해석하는 것이 좋습니다. "
            "OI와 거래량이 다시 증가하는지 확인해야 합니다."
        )

    if conviction in ["Low", "Medium-Low"]:
        return (
            "기존 리서치 시그널과 실시간 파생 데이터의 정렬이 약한 구간입니다. "
            "방향성 판단보다는 다음 데이터 업데이트를 기다리는 관망 우위 구간입니다."
        )

    return (
        "현재는 명확한 추세 확정보다는 주요 지표의 다음 변화를 확인해야 하는 구간입니다. "
        "가격, OI, Funding, Long/Short Ratio를 함께 추적해야 합니다."
    )


def build_final_summary_section(overlay, trading_context):
    """
    리포트 마지막에 붙일 Final Research Summary 섹션 생성.
    """
    overlay_status = get_overlay_status(overlay)
    risk_flags = get_risk_flags(trading_context)

    conviction = classify_conviction(overlay_status, risk_flags)
    main_risk = identify_main_risk(risk_flags)
    overall_view = build_overall_view(overlay, trading_context)
    best_action = suggest_best_action(overlay_status, conviction, risk_flags)

    risk_flags_text = ", ".join(risk_flags) if risk_flags else "None"

    return f"""
---

## 10. Final Research Summary

### 10.1 Overall View

{overall_view}

### 10.2 Conviction

- Conviction Level: {conviction}
- Overlay Status: {overlay_status}
- Active Risk Flags: {risk_flags_text}

### 10.3 Main Risk

{main_risk}

### 10.4 Best Research Action

{best_action}

### 10.5 Final Conclusion

현재 리서치 결론은 기존 CSV 기반 Research Agent 결과와 Trading Bot의 실시간 파생 데이터 context를 함께 반영한 것입니다.  
다음 업데이트에서는 가격 변화, OI 변화, Long/Short Ratio, liquidation_24h, Funding Rate의 조합이 같은 방향으로 정렬되는지 확인하는 것이 핵심입니다.
""".strip()