from tools.price_tool import get_price_data
from tools.funding_tool import get_funding_rate
from tools.oi_tool import get_open_interest


class MarketAgent:
    def __init__(self, symbol: str):
        self.symbol = symbol

    def analyze_market(self) -> dict:
        price_data = get_price_data(self.symbol)
        funding_data = get_funding_rate(self.symbol)
        oi_data = get_open_interest(self.symbol)

        rule_based_summary = self._interpret_market(
            price_change_percent=price_data.get("price_change_percent"),
            funding_rate=funding_data.get("funding_rate"),
            open_interest=oi_data.get("open_interest"),
        )

        return {
            "symbol": self.symbol,
            "price_data": price_data,
            "funding_data": funding_data,
            "open_interest_data": oi_data,
            "rule_based_summary": rule_based_summary,
        }

    def _interpret_market(
        self,
        price_change_percent: float | None,
        funding_rate: float | None,
        open_interest: float | None,
    ) -> str:
        if price_change_percent is None or funding_rate is None or open_interest is None:
            return "일부 시장 데이터가 누락되어 제한적인 해석만 가능합니다."

        if price_change_percent > 0 and funding_rate > 0:
            return "가격 상승과 양수 펀딩비가 함께 나타나고 있어 롱 포지션 유입 가능성이 있습니다."

        if price_change_percent < 0 and funding_rate > 0:
            return "가격은 하락했지만 펀딩비가 양수입니다. 롱 포지션이 아직 정리되지 않았을 수 있습니다."

        if price_change_percent > 0 and funding_rate < 0:
            return "가격은 상승했지만 펀딩비가 음수입니다. 숏 스퀴즈 가능성을 관찰할 필요가 있습니다."

        if price_change_percent < 0 and funding_rate < 0:
            return "가격 하락과 음수 펀딩비가 함께 나타나고 있어 숏 우위 심리가 강할 수 있습니다."

        return "현재 시장은 뚜렷한 방향성보다 중립적인 상태에 가깝습니다."
