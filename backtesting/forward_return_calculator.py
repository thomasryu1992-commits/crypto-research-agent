def add_forward_returns(scored_rows: list[dict], windows: list[int]) -> list[dict]:
    rows = [dict(r) for r in scored_rows]

    for i, row in enumerate(rows):
        current_close = row.get("close")

        for window in windows:
            future_index = i + window

            if future_index >= len(rows) or current_close is None or current_close == 0:
                row[f"forward_return_{window}"] = None
                continue

            future_close = rows[future_index].get("close")
            row[f"forward_return_{window}"] = _pct_change(current_close, future_close)

    return rows


def _pct_change(old, new):
    try:
        if old is None or new is None or float(old) == 0:
            return None
        return ((float(new) - float(old)) / float(old)) * 100
    except (TypeError, ValueError, ZeroDivisionError):
        return None
