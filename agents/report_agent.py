from services.llm_service import ask_llm
from tools.telegram_tool import send_telegram_message
from memory.report_memory import save_report
from config import REPORT_LANGUAGE


class ReportAgent:
    def generate_report(self, market_data: dict) -> str:
        prompt = self._build_prompt(market_data)
        report = ask_llm(prompt)

        saved_path = save_report(report)
        print(f"Report saved: {saved_path}")

        telegram_result = send_telegram_message(report)
        if telegram_result.get("sent"):
            print("Telegram message sent successfully.")
        else:
            print(f"Telegram skipped or failed: {telegram_result.get('reason')}")

        return report

    def _build_prompt(self, market_data: dict) -> str:
        language_instruction = "한국어로 작성해줘." if REPORT_LANGUAGE == "ko" else "Write in English."

        return f"""
너는 크립토 시장을 분석하는 리서치 애널리스트야.

아래 시장 데이터를 바탕으로 Daily Crypto Research Report를 작성해줘.

작성 언어:
{language_instruction}

리포트 형식:
1. 시장 요약
2. BTC 현재 상태
3. 선물 시장 분석
4. Funding Rate 해석
5. Open Interest 해석
6. 오늘의 핵심 리스크
7. 관찰해야 할 포인트
8. 결론

주의사항:
- 투자 조언처럼 단정하지 말고, 데이터 기반 시나리오로 설명해.
- 초보자도 이해할 수 있게 쉽게 설명해.
- 하지만 리서치 리포트처럼 전문적인 톤은 유지해.
- 가격, 펀딩비, OI를 서로 연결해서 해석해.
- 마지막에는 "오늘의 핵심 체크포인트"를 bullet로 정리해.

시장 데이터:
{market_data}
""".strip()
