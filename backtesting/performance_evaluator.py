def evaluate_backtest(rows: list[dict], primary_window: int) -> dict:
    valid = [r for r in rows if r.get(f"forward_return_{primary_window}") is not None]

    if not valid:
        return {"error": "No valid forward returns."}

    directional_hits = 0
    directional_total = 0

    bullish = []
    bearish = []
    constructive = []
    risk_off = []
    neutral = []

    for row in valid:
        bias = row.get("bias")
        fwd = row.get(f"forward_return_{primary_window}")

        if bias in ["Bullish", "Strong Bullish"]:
            bullish.append(fwd)
            directional_total += 1
            if fwd > 0:
                directional_hits += 1

        elif bias in ["Bearish", "Strong Bearish"]:
            bearish.append(fwd)
            directional_total += 1
            if fwd < 0:
                directional_hits += 1

        elif bias == "Constructive":
            constructive.append(fwd)

        elif bias == "Risk-Off":
            risk_off.append(fwd)

        else:
            neutral.append(fwd)

    direction_accuracy = directional_hits / directional_total if directional_total else None

    return {
        "primary_window": primary_window,
        "sample_count": len(valid),
        "directional_signal_count": directional_total,
        "direction_accuracy": direction_accuracy,
        "bullish_signal_count": len(bullish),
        "bearish_signal_count": len(bearish),
        "constructive_signal_count": len(constructive),
        "risk_off_signal_count": len(risk_off),
        "neutral_signal_count": len(neutral),
        "avg_forward_return_all": _avg([r.get(f"forward_return_{primary_window}") for r in valid]),
        "avg_forward_return_bullish": _avg(bullish),
        "avg_forward_return_bearish": _avg(bearish),
        "avg_forward_return_constructive": _avg(constructive),
        "avg_forward_return_risk_off": _avg(risk_off),
        "avg_forward_return_neutral": _avg(neutral),
        "hit_rate_bullish": _hit_rate(bullish, "positive"),
        "hit_rate_bearish": _hit_rate(bearish, "negative"),
        "score_bucket_summary": _score_bucket_summary(valid, primary_window),
        "scenario_summary": _group_summary(valid, primary_window, "scenario"),
        "bias_summary": _group_summary(valid, primary_window, "bias"),
        "signal_quality_summary": _group_summary(valid, primary_window, "signal_quality"),
        "signal_quality_label_summary": _group_summary(valid, primary_window, "signal_quality_label"),
        "signal_timing_summary": _group_summary(valid, primary_window, "signal_timing"),
        "signal_timing_label_summary": _group_summary(valid, primary_window, "signal_timing_label"),
    }


def _avg(values):
    values = [v for v in values if v is not None]
    if not values:
        return None
    return sum(values) / len(values)


def _hit_rate(values, direction: str):
    values = [v for v in values if v is not None]
    if not values:
        return None

    if direction == "positive":
        return sum(1 for v in values if v > 0) / len(values)

    if direction == "negative":
        return sum(1 for v in values if v < 0) / len(values)

    return None


def _score_bucket_summary(rows, window):
    buckets = {
        "strong_bullish_score": [],
        "bullish_score": [],
        "neutral_score": [],
        "bearish_score": [],
        "strong_bearish_score": [],
    }

    for r in rows:
        score = r.get("final_score", 0)
        fwd = r.get(f"forward_return_{window}")

        if fwd is None:
            continue

        if score >= 0.60:
            buckets["strong_bullish_score"].append(fwd)
        elif score >= 0.25:
            buckets["bullish_score"].append(fwd)
        elif score <= -0.60:
            buckets["strong_bearish_score"].append(fwd)
        elif score <= -0.25:
            buckets["bearish_score"].append(fwd)
        else:
            buckets["neutral_score"].append(fwd)

    return {
        key: {
            "count": len(values),
            "avg_forward_return": _avg(values),
            "positive_rate": _hit_rate(values, "positive"),
            "negative_rate": _hit_rate(values, "negative"),
        }
        for key, values in buckets.items()
    }


def _group_summary(rows, window, key):
    grouped = {}

    for r in rows:
        group_key = r.get(key, "Unknown")
        if group_key is None or group_key == "":
            group_key = "Unknown"
        grouped.setdefault(group_key, []).append(r.get(f"forward_return_{window}"))

    return {
        group_key: {
            "count": len(values),
            "avg_forward_return": _avg(values),
            "positive_rate": _hit_rate(values, "positive"),
            "negative_rate": _hit_rate(values, "negative"),
        }
        for group_key, values in grouped.items()
    }
