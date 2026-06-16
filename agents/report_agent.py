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
너는 크립토 선물 시장을 분석하는 트레이딩 리서치 애널리스트야.

아래 시장 데이터를 바탕으로 BTC Daily Trading Research Report를 작성해줘.

작성 언어:
{language_instruction}

가장 중요한 목표:
이 리포트는 단순 시장 요약이 아니라, 실제 트레이딩 의사결정에 참고할 수 있는 시나리오 리포트여야 한다.

반드시 지켜야 할 원칙:
- 단정적인 매수/매도 지시는 하지 않는다.
- "조건이 충족되면 어떤 시나리오가 유효한지" 중심으로 작성한다.
- 가격, Funding Rate, Open Interest를 각각 따로 설명하지 말고 서로 연결해서 해석한다.
- Funding Rate만 보고 숏 스퀴즈를 단정하지 않는다.
- Open Interest만 보고 방향성을 단정하지 않는다.
- 항상 Long Scenario, Short Scenario, Invalidation을 포함한다.
- 초보자도 이해할 수 있게 쓰되, 트레이딩 리서치 톤을 유지한다.
- 반복적인 문장은 피하고, 실행 가능한 관찰 포인트를 제시한다.
- 수치가 주어지면 가능한 한 수치를 활용한다.
- 알 수 없는 지지선/저항선 가격을 임의로 만들지 말고, "직전 고점", "단기 저항", "현재 가격대", "주요 지지 구간"처럼 표현한다.

리포트 형식:

# Daily BTC Trading Research Report

## 1. Market Bias
현재 시장 방향성을 중립 / 약상방 / 강상방 / 약하방 / 강하방 중 하나로 판단하고, 이유를 설명해.

## 2. Current Market Structure
현재 가격 흐름을 설명해.
가격 상승/하락, 현물과 선물 가격 차이, 시장 분위기를 연결해서 해석해.

## 3. Futures Positioning
Funding Rate와 Open Interest를 함께 해석해.
다음 조합을 참고해:
- 가격 상승 + Funding 양수 + OI 증가 = 롱 과열 가능성
- 가격 상승 + Funding 음수 + OI 유지/증가 = 숏 압박 또는 숏 스퀴즈 가능성
- 가격 하락 + Funding 양수 + OI 증가 = 롱 포지션 갇힘 가능성
- 가격 하락 + Funding 음수 + OI 증가 = 숏 우위 추세 가능성
- 가격 상승 + OI 감소 = 숏 커버링 가능성
- 가격 하락 + OI 감소 = 롱 청산 또는 디레버리징 가능성

## 4. Long Scenario
어떤 조건이 충족되면 롱 시나리오가 유효해지는지 설명해.
반드시 다음을 포함해:
- 확인 조건
- 진입을 고려할 수 있는 상황
- 추격 진입을 피해야 하는 이유
- 리스크

## 5. Short Scenario
어떤 조건이 충족되면 숏 시나리오가 유효해지는지 설명해.
반드시 다음을 포함해:
- 확인 조건
- 반등 실패 조건
- 지지선 이탈 시 해석
- 리스크

## 6. Invalidation
롱 관점과 숏 관점이 각각 어떤 조건에서 무효화되는지 설명해.

## 7. Risk Level
현재 리스크를 Low / Medium / High 중 하나로 분류해.
그 이유를 가격, Funding, OI 조합으로 설명해.

## 8. Trading Plan
오늘 관찰해야 할 행동 계획을 작성해.
단, 직접적인 매수/매도 지시가 아니라 조건부 대응 계획으로 작성해.

## 9. Key Checkpoints
마지막에 오늘 체크해야 할 핵심 포인트를 bullet로 정리해.

시장 데이터:
{market_data}
""".strip()
