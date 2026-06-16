from tools.price_tool import get_price_data
from tools.funding_tool import get_funding_rate
from tools.oi_tool import get_open_interest
from tools.candle_tool import get_recent_futures_candles, summarize_candles
from services.market_context_builder import build_market_context
from memory.market_snapshot import load_latest_snapshot, save_market_snapshot


class MarketAgent:
    def __init__(self, symbol: str):
        self.symbol = symbol

    def analyze_market(self) -> dict:
        price_data = get_price_data(self.symbol)
        funding_data = get_funding_rate(self.symbol)
        oi_data = get_open_interest(self.symbol)

        candles = get_recent_futures_candles(symbol=self.symbol, interval="1h", limit=24)
        candle_summary = summarize_candles(candles)

        current_snapshot = {
            "symbol": self.symbol,
            "price": price_data.get("last_price"),
            "price_change_percent_24h": price_data.get("price_change_percent"),
            "high_price_24h": price_data.get("high_price"),
            "low_price_24h": price_data.get("low_price"),
            "volume_24h": price_data.get("volume"),
            "quote_volume_24h": price_data.get("quote_volume"),
            "funding_rate": funding_data.get("funding_rate"),
            "open_interest": oi_data.get("open_interest"),
            "mark_price": funding_data.get("mark_price"),
            "index_price": funding_data.get("index_price"),
            "candle_summary": candle_summary,
        }

        previous_snapshot = load_latest_snapshot(self.symbol)
        delta = self._calculate_delta(current_snapshot, previous_snapshot)

        market_context = build_market_context(
            snapshot=current_snapshot,
            delta=delta,
            previous_snapshot=previous_snapshot,
        )

        save_market_snapshot(self.symbol, current_snapshot)

        return {
            "symbol": self.symbol,
            "price_data": price_data,
            "funding_data": funding_data,
            "open_interest_data": oi_data,
            "candle_summary": candle_summary,
            "current_snapshot": current_snapshot,
            "previous_snapshot": previous_snapshot,
            "delta": delta,
            "market_context": market_context,
        }

    def _calculate_delta(self, current: dict, previous: dict | None) -> dict:
        if not previous:
            return {
                "has_previous_snapshot": False,
                "message": "이전 스냅샷이 없어 변화율 계산은 다음 실행부터 가능합니다.",
            }

        return {
            "has_previous_snapshot": True,
            "price_change_since_last_snapshot": self._pct_change(previous.get("price"), current.get("price")),
            "funding_change_since_last_snapshot": self._absolute_change(previous.get("funding_rate"), current.get("funding_rate")),
            "open_interest_change_since_last_snapshot": self._pct_change(previous.get("open_interest"), current.get("open_interest")),
            "volume_change_since_last_snapshot": self._pct_change(previous.get("volume_24h"), current.get("volume_24h")),
        }

    def _pct_change(self, old, new):
        try:
            if old is None or new is None or float(old) == 0:
                return None
            return ((float(new) - float(old)) / float(old)) * 100
        except (TypeError, ValueError, ZeroDivisionError):
            return None

    def _absolute_change(self, old, new):
        try:
            if old is None or new is None:
                return None
            return float(new) - float(old)
        except (TypeError, ValueError):
            return None
