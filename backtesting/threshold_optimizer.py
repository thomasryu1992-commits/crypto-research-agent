from scenarios.scenario_engine import classify_scenario
from backtesting.forward_return_calculator import add_forward_returns
from backtesting.performance_evaluator import evaluate_backtest


def optimize_thresholds(scored_rows: list[dict], timeframe: str, primary_window: int) -> tuple[list[dict], dict]:
    candidates = _build_candidates(timeframe)
    results = []

    for calibration in candidates:
        classified_rows = []
        wrapper = {timeframe: calibration}

        for row in scored_rows:
            scenario = classify_scenario(row, timeframe, wrapper)
            classified_rows.append({**row, **scenario})

        rows_with_forward = add_forward_returns(classified_rows, [primary_window])
        evaluation = evaluate_backtest(rows_with_forward, primary_window)
        objective = _objective_score(evaluation, timeframe)

        result = {
            **calibration,
            "objective_score": objective,
            "sample_count": evaluation.get("sample_count"),
            "directional_signal_count": evaluation.get("directional_signal_count"),
            "direction_accuracy": evaluation.get("direction_accuracy"),
            "bullish_signal_count": evaluation.get("bullish_signal_count"),
            "bearish_signal_count": evaluation.get("bearish_signal_count"),
            "constructive_signal_count": evaluation.get("constructive_signal_count"),
            "risk_off_signal_count": evaluation.get("risk_off_signal_count"),
            "neutral_signal_count": evaluation.get("neutral_signal_count"),
            "avg_forward_return_all": evaluation.get("avg_forward_return_all"),
            "avg_forward_return_bullish": evaluation.get("avg_forward_return_bullish"),
            "avg_forward_return_bearish": evaluation.get("avg_forward_return_bearish"),
            "avg_forward_return_constructive": evaluation.get("avg_forward_return_constructive"),
            "avg_forward_return_risk_off": evaluation.get("avg_forward_return_risk_off"),
            "avg_forward_return_neutral": evaluation.get("avg_forward_return_neutral"),
            "hit_rate_bullish": evaluation.get("hit_rate_bullish"),
            "hit_rate_bearish": evaluation.get("hit_rate_bearish"),
        }
        results.append(result)

    results.sort(key=lambda x: x.get("objective_score", -999), reverse=True)
    best = results[0] if results else {}

    best_calibration = {
        timeframe: {
            "bullish_threshold": best.get("bullish_threshold"),
            "constructive_threshold": best.get("constructive_threshold"),
            "risk_off_threshold": best.get("risk_off_threshold"),
            "bearish_threshold": best.get("bearish_threshold"),
            "market_confirm_threshold": best.get("market_confirm_threshold"),
            "market_bearish_confirm_threshold": best.get("market_bearish_confirm_threshold"),
        },
        "metadata": {
            "timeframe": timeframe,
            "primary_window": primary_window,
            "objective_score": best.get("objective_score"),
            "direction_accuracy": best.get("direction_accuracy"),
            "bullish_signal_count": best.get("bullish_signal_count"),
            "bearish_signal_count": best.get("bearish_signal_count"),
            "avg_forward_return_bullish": best.get("avg_forward_return_bullish"),
            "avg_forward_return_bearish": best.get("avg_forward_return_bearish"),
            "warning": "Optimized on historical data. Validate out-of-sample before relying on it.",
        },
    }

    return results, best_calibration


def _build_candidates(timeframe: str) -> list[dict]:
    candidates = []

    if timeframe == "weekly":
        bullish_values = [0.25, 0.30, 0.35, 0.40, 0.45]
        constructive_values = [0.15, 0.20, 0.25]
        risk_off_values = [-0.20, -0.25, -0.30]
        bearish_values = [-0.45, -0.55, -0.60, -0.70]
        market_confirm_values = [0.15, 0.20, 0.25, 0.30]
        market_bearish_values = [-0.20, -0.30, -0.40]
    else:
        bullish_values = [0.30, 0.35, 0.40, 0.45, 0.50]
        constructive_values = [0.15, 0.20, 0.25, 0.30]
        risk_off_values = [-0.15, -0.20, -0.25, -0.30]
        bearish_values = [-0.30, -0.35, -0.40, -0.45, -0.50]
        market_confirm_values = [0.05, 0.10, 0.15, 0.20]
        market_bearish_values = [-0.05, -0.10, -0.15, -0.20]

    for bullish in bullish_values:
        for constructive in constructive_values:
            if constructive >= bullish:
                continue
            for risk_off in risk_off_values:
                for bearish in bearish_values:
                    if bearish >= risk_off:
                        continue
                    for market_confirm in market_confirm_values:
                        for market_bearish in market_bearish_values:
                            candidates.append({
                                "bullish_threshold": bullish,
                                "constructive_threshold": constructive,
                                "risk_off_threshold": risk_off,
                                "bearish_threshold": bearish,
                                "market_confirm_threshold": market_confirm,
                                "market_bearish_confirm_threshold": market_bearish,
                            })

    return candidates


def _objective_score(evaluation: dict, timeframe: str) -> float:
    bullish_count = evaluation.get("bullish_signal_count") or 0
    bearish_count = evaluation.get("bearish_signal_count") or 0
    directional_count = evaluation.get("directional_signal_count") or 0

    avg_bull = evaluation.get("avg_forward_return_bullish")
    avg_bear = evaluation.get("avg_forward_return_bearish")
    avg_neutral = evaluation.get("avg_forward_return_neutral")
    avg_risk_off = evaluation.get("avg_forward_return_risk_off")
    direction_accuracy = evaluation.get("direction_accuracy")

    score = 0.0

    if avg_bull is not None:
        score += avg_bull * 1.2

    if avg_neutral is not None and avg_bull is not None:
        score += (avg_bull - avg_neutral) * 0.8

    if avg_bear is not None and avg_neutral is not None:
        score += (avg_neutral - avg_bear) * 0.8

    if avg_risk_off is not None and avg_neutral is not None:
        score += (avg_neutral - avg_risk_off) * 0.5

    if direction_accuracy is not None:
        score += (direction_accuracy - 0.5) * 10

    min_bull = 20 if timeframe == "daily" else 10
    min_bear = 10 if timeframe == "daily" else 5

    if bullish_count < min_bull:
        score -= (min_bull - bullish_count) * 0.5

    if bearish_count < min_bear:
        score -= (min_bear - bearish_count) * 0.4

    if directional_count < (min_bull + min_bear):
        score -= 5

    return round(score, 6)
