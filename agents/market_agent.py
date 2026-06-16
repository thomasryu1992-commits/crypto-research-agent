from tools.price_tool import get_price_data
from tools.funding_tool import get_funding_rate
from tools.oi_tool import get_open_interest
from tools.candle_tool import get_recent_futures_candles, summarize_candles
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

        save_market_snapshot(self.symbol, current_snapshot)

        rule_based_summary = self._interpret_market(current_snapshot, delta)

        return {
            "symbol": self.symbol,
            "price_data": price_data,
            "funding_data": funding_data,
            "open_interest_data": oi_data,
            "candle_summary": candle_summary,
            "current_snapshot": current_snapshot,
            "previous_snapshot": previous_snapshot,
            "delta": delta,
            "rule_based_summary": rule_based_summary,
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

    def _interpret_market(self, snapshot: dict, delta: dict) -> str:
        price_change_24h = snapshot.get("price_change_percent_24h")
        funding = snapshot.get("funding_rate")
        oi_change = delta.get("open_interest_change_since_last_snapshot")
        candle_trend = snapshot.get("candle_summary", {}).get("trend")

        if price_change_24h is None or funding is None:
            return "가격 또는 펀딩 데이터가 부족해 제한적인 해석만 가능합니다."

        if not delta.get("has_previous_snapshot"):
            if price_change_24h > 0 and funding < 0:
                return "가격은 상승 중이나 펀딩비가 음수입니다. 시장이 상승을 완전히 신뢰하지 않거나 숏 포지션이 누적되어 있을 수 있습니다."
            if price_change_24h > 0 and funding > 0:
                return "가격 상승과 양수 펀딩이 함께 나타나고 있습니다. 롱 포지션 과열 여부를 관찰해야 합니다."
            if price_change_24h < 0 and funding > 0:
                return "가격 하락에도 펀딩이 양수입니다. 롱 포지션이 아직 충분히 정리되지 않았을 가능성이 있습니다."
            if price_change_24h < 0 and funding < 0:
                return "가격 하락과 음수 펀딩이 함께 나타납니다. 숏 우위 추세가 이어질 수 있습니다."
            return "현재 시장은 중립적이며 추가 데이터 확인이 필요합니다."

        if price_change_24h > 0 and funding < 0 and oi_change is not None and oi_change >= 0:
            return "가격 상승, 음수 펀딩, OI 유지/증가 조합입니다. 숏 포지션 압박 또는 숏 스퀴즈 가능성을 관찰할 수 있습니다."
        if price_change_24h > 0 and funding > 0 and oi_change is not None and oi_change > 0:
            return "가격 상승, 양수 펀딩, OI 증가 조합입니다. 롱 포지션 유입이 강하지만 단기 과열 리스크도 커질 수 있습니다."
        if price_change_24h < 0 and funding > 0 and oi_change is not None and oi_change > 0:
            return "가격 하락, 양수 펀딩, OI 증가 조합입니다. 롱 포지션이 갇히는 구조일 수 있어 롱 청산 리스크를 관찰해야 합니다."
        if price_change_24h < 0 and funding < 0 and oi_change is not None and oi_change > 0:
            return "가격 하락, 음수 펀딩, OI 증가 조합입니다. 신규 숏 유입 또는 숏 우위 추세 가능성이 있습니다."

        return f"현재 캔들 흐름은 {candle_trend}에 가깝고, 가격·펀딩·OI 조합을 추가로 관찰해야 합니다."
