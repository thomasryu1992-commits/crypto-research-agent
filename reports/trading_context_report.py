
from scenarios.context_overlay_engine import build_context_overlay

def format_number(value):
    try:
        if value == "" or value is None:
            return "N/A"

        value = float(value)

        if abs(value) >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"

        if abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"

        if abs(value) >= 1_000:
            return f"{value:,.2f}"

        return f"{value:.4f}"

    except Exception:
        return str(value)


def build_flag_interpretation(risk_flags):
    if not risk_flags:
        return "No major real-time derivatives risk flags detected."

    interpretations = []

    if "long_crowding" in risk_flags or "extreme_long_crowding" in risk_flags:
        interpretations.append(
            "Long positioning is crowded. If BTC loses key support, long liquidation pressure can increase."
        )

    if "crowded_long_with_leverage" in risk_flags:
        interpretations.append(
            "Long crowding is combined with leverage expansion, which increases downside liquidation risk."
        )

    if "healthy_positive_funding" in risk_flags:
        interpretations.append(
            "Funding is positive but not overheated, which can support trend continuation if price structure remains firm."
        )

    if "funding_overheated" in risk_flags:
        interpretations.append(
            "Funding appears overheated, suggesting crowded upside positioning and higher reversal risk."
        )

    if "trend_participation" in risk_flags:
        interpretations.append(
            "Price and OI are rising together, suggesting new position participation in the current move."
        )

    if "short_covering_rebound" in risk_flags:
        interpretations.append(
            "Price is rising while OI is falling, which may indicate a short-covering rebound rather than strong new demand."
        )

    if "trapped_longs" in risk_flags:
        interpretations.append(
            "Price is falling while OI is rising, suggesting long positions may be trapped."
        )

    if "position_flush" in risk_flags or "deleveraging" in risk_flags:
        interpretations.append(
            "Positioning is being reduced, which can indicate deleveraging or post-liquidation reset."
        )

    if "liquidation_spike" in risk_flags:
        interpretations.append(
            "Liquidation activity is elevated, so short-term volatility risk is high."
        )

    if "liquidation_watch" in risk_flags:
        interpretations.append(
            "Liquidation activity is notable and should be monitored for acceleration."
        )

    if not interpretations:
        return "Risk flags are present, but no dominant interpretation rule was triggered."

    return "\n".join([f"- {item}" for item in interpretations])


def build_trading_context_section(context, latest_row=None):
    """
    Trading Bot의 latest_btc_research_context.json을 기존 V3 report 뒤에 붙일 섹션으로 변환.
    latest_row를 함께 받으면 기존 Research Agent 방향성과 실시간 Trading Context를 비교한다.
    """
    if not context:
        return """
---

## 9. Real-Time Trading Context

No Trading Bot context file was found.  
The report is based only on the existing V3 CSV-based research pipeline.
""".strip()

    metadata = context.get("metadata", {})
    asset = context.get("asset", {})
    market_state = context.get("market_state", {})
    key_metrics = context.get("key_metrics", {})
    risk_flags = context.get("risk_flags", [])
    classified = context.get("classified_evidence", {})

    bullish_evidence = classified.get("bullish_evidence", [])
    bearish_evidence = classified.get("bearish_evidence", [])
    reset_evidence = classified.get("reset_or_uncertain_evidence", [])

    flag_text = ", ".join(risk_flags) if risk_flags else "None"
    bullish_text = ", ".join(bullish_evidence) if bullish_evidence else "None"
    bearish_text = ", ".join(bearish_evidence) if bearish_evidence else "None"
    reset_text = ", ".join(reset_evidence) if reset_evidence else "None"

    flag_interpretation = build_flag_interpretation(risk_flags)
    overlay = build_context_overlay(latest_row, context)

    watch_conditions = overlay.get("watch_conditions", [])

    return f"""
---

## 9. Real-Time Trading Context

Source: {metadata.get("source")}
Generated At: {metadata.get("generated_at")}
Asset: {asset.get("symbol")}

### 9.1 Current Market State

- Trading Bot Market State: {market_state.get("market_state")}
- Trading Bot Market Score: {market_state.get("market_score")}
- Trading Bot Market Bias: {market_state.get("market_bias")}

### 9.2 Real-Time Key Metrics

- BTC Price: {format_number(key_metrics.get("price"))}
- 24H Price Change: {format_number(key_metrics.get("price_change_24h"))}%
- Funding Rate: {key_metrics.get("funding_rate")}
- Open Interest: {format_number(key_metrics.get("open_interest"))}
- OI Change 4H: {format_number(key_metrics.get("oi_change_4h"))}%
- Long/Short Ratio: {format_number(key_metrics.get("long_short_ratio"))}
- 24H Liquidation: {format_number(key_metrics.get("liquidation_24h"))}
- 24H Volume: {format_number(key_metrics.get("volume_24h"))}

### 9.3 Risk Flags

{flag_text}

### 9.4 Evidence Classification

- Bullish Evidence: {bullish_text}
- Bearish Evidence: {bearish_text}
- Reset / Uncertain Evidence: {reset_text}

### 9.5 Real-Time Interpretation

{flag_interpretation}

### 9.6 Context Overlay

- Existing Research Direction: {overlay.get("research_direction")}
- Trading Context Direction: {overlay.get("trading_context_direction")}
- Overlay Status: {overlay.get("overlay_status")}

{overlay.get("overlay_summary")}

### 9.7 Scenario Overlay

Base Scenario:
{overlay.get("base_scenario")}

Bullish Scenario:
{overlay.get("bullish_scenario")}

Bearish Scenario:
{overlay.get("bearish_scenario")}

### 9.8 Watch Conditions

{chr(10).join([f"- {item}" for item in watch_conditions])}
""".strip()

def build_trading_context_section_with_overlay(context, latest_row=None):
    """
    Trading context section과 overlay dict를 함께 반환한다.
    main.py에서 Final Summary Engine이 overlay를 재사용할 수 있게 한다.
    """
    overlay = build_context_overlay(latest_row, context) if context else None
    section = build_trading_context_section(context, latest_row)

    return section, overlay