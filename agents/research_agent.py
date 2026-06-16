from agents.market_agent import MarketAgent
from agents.report_agent import ReportAgent
from config import DEFAULT_SYMBOL


class CryptoResearchAgent:
    def __init__(self, symbol: str = DEFAULT_SYMBOL):
        self.symbol = symbol
        self.market_agent = MarketAgent(symbol=symbol)
        self.report_agent = ReportAgent()

    def run_daily_research(self) -> str:
        market_data = self.market_agent.analyze_market()
        report = self.report_agent.generate_report(market_data=market_data)
        return report
