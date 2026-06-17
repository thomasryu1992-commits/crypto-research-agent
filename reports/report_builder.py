def build_latest_report(row: dict, timeframe: str) -> str:
    context = row.get("metric_context", {})

    report = f"""
# BTC {timeframe.upper()} Crypto Market Research Report - V3.6

## 1. Executive Summary
Date: {row.get("date")}
BTC Close: {row.get("close")}

Final Score: {row.get("final_score")}
Bias: {row.get("bias")}
Scenario: {row.get("scenario")}
Confidence: {row.get("confidence")}

Signal Quality: {row.get("signal_quality")} - {row.get("signal_quality_label")}
Confirmations: {row.get("confirmation_count")}
Warnings: {row.get("warning_count")}
Reasons: {row.get("signal_reasons")}

## 2. Core Category Scores
- Market Structure Score: {row.get("market_structure_score")}
- Derivatives Positioning Score: {row.get("derivatives_positioning_score")}
- CVD Flow Score: {row.get("cvd_flow_score")}
- Volume Score: {row.get("volume_score")}

## 3. External Data Scores
- ETF / Institutional Flow Score: {row.get("etf_institutional_flow_score")}
- Exchange Flow Score: {row.get("exchange_flow_score")}
- Stablecoin Liquidity Score: {row.get("stablecoin_liquidity_score")}
- Valuation / Cycle Score: {row.get("valuation_cycle_score")}
- Network Activity Score: {row.get("network_activity_score")}

## 4. Market Metrics
- Return 1 Period: {context.get("return_1")}
- Return 3 Periods: {context.get("return_3")}
- Return 7 Periods: {context.get("return_7")}
- Return 14 Periods: {context.get("return_14")}
- Return 30 Periods: {context.get("return_30")}
- RSI: {context.get("rsi")}

## 5. Positioning / Flow Metrics
- OI Change 3 Periods: {context.get("oi_change_3")}
- OI Change 7 Periods: {context.get("oi_change_7")}
- CVD Change 3 Periods: {context.get("cvd_change_3")}
- CVD Change 7 Periods: {context.get("cvd_change_7")}
- Volume Change 3 Periods: {context.get("volume_change_3")}
- Volume Change 7 Periods: {context.get("volume_change_7")}

## 6. External Metrics
- Total BTC ETF Net Flow: {context.get("total_btc_etf_netflow")}
- IBIT Net Flow: {context.get("ibit_netflow")}
- ETF 5D Net Flow: {context.get("etf_5d_netflow")}
- Exchange Netflow: {context.get("exchange_netflow")}
- Exchange Reserve: {context.get("exchange_reserve")}
- Stablecoin Supply: {context.get("stablecoin_supply")}
- Stablecoin Exchange Reserve: {context.get("stablecoin_exchange_reserve")}
- MVRV: {context.get("mvrv")}
- SOPR: {context.get("sopr")}
- Active Addresses: {context.get("active_addresses")}
- Transaction Count: {context.get("tx_count")}

## 7. Signal Quality Interpretation
A = High-quality upside setup
B = Constructive / early upside candidate
C = Positive but incomplete confirmation
D = Risk-Off / upside weakening
F = Bearish / downside pressure
N = Neutral / no edge

## 8. Conclusion
V3.6 separates early upside candidates from confirmed bullish signals.
Bullish is stricter, while Constructive is treated as a potential early upside signal.
"""

    return report.strip()
