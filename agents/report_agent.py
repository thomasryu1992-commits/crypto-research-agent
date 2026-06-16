from services.llm_service import ask_llm
from services.report_post_processor import clean_report_language
from services.market_interpreter import build_market_interpretation
from tools.telegram_tool import send_telegram_message
from memory.report_memory import save_report
from config import REPORT_LANGUAGE, SEND_TELEGRAM


class ReportAgent:
    def generate_report(self, market_data: dict) -> str:
        market_interpretation = build_market_interpretation(market_data)
        prompt = self._build_prompt(market_data, market_interpretation)

        raw_report = ask_llm(prompt)
        report = clean_report_language(raw_report)

        print("V2.5.2 trading plan separation applied")
        print("V2.5.1 risk text fix applied")
        print("V2.5 key levels applied")
        print("V2.5 invalidation logic applied")
        print("V2.5 post processor applied")

        saved_path = save_report(report)
        print(f"Report saved: {saved_path}")

        if SEND_TELEGRAM:
            telegram_result = send_telegram_message(report)

            if telegram_result.get("sent"):
                print("Telegram message sent successfully.")
            else:
                print(f"Telegram skipped or failed: {telegram_result.get('reason')}")
        else:
            print("Telegram skipped: SEND_TELEGRAM=false")

        return report

    def _build_prompt(self, market_data: dict, market_interpretation: dict) -> str:
        language_instruction = (
            "한국어로 작성해줘."
            if REPORT_LANGUAGE == "ko"
            else "Write in English."
        )

        prompt = f"""
너는 크립토 선물 시장 리서치 애널리스트다.

아래 Python 해석값을 바탕으로 완성된 리포트만 작성해라.
숫자, Funding Rate 부호, OI 변화율, 지지/저항 구간은 반드시 Python 해석값을 그대로 사용해라.
네가 숫자를 다시 계산하거나 가격 구간을 새로 만들지 마라.

작성 언어:
{language_instruction}

절대 금지:
- 프롬프트 지시문을 출력하지 마라.
- "반드시 포함", "자연스럽게 설명해", "기준으로 판단한다" 같은 문장을 출력하지 마라.
- 매수/매도 지시를 하지 마라.
- "진입합니다", "청산합니다", "진입을 고려합니다"를 쓰지 마라.
- OI를 롱/숏으로 구분하지 마라.
- 가격 레벨을 임의로 만들지 마라.
- Invalidation 내용을 Trading Plan에 섞지 마라.

필수 표현:
- 시장 전체 OI
- 상방 시나리오가 강화됩니다
- 하방 시나리오가 강화됩니다
- 추격 진입보다 확인 매매가 우선입니다
- 참고 저항 구간
- 참고 지지 구간

Python 해석값:
{market_interpretation}

원본 시장 데이터:
{market_data}

작성 규칙:
- Risk & Invalidation 섹션에서는 Python 해석값의 invalidation만 사용해라.
- Trading Plan 섹션에서는 Python 해석값의 trading_plan만 사용해라.
- Trading Plan에는 "회복 실패", "유지 실패", "마감 실패", "약화", "Invalidation"이라는 표현을 쓰지 마라.
- Trading Plan은 상방 대응, 하방 대응, 대기 조건 3개로만 작성해라.

아래 형식으로만 작성해라.

# Daily BTC Trading Research Report

## 1. Market Bias
Python 해석값의 bias_text를 바탕으로 한 문단으로 작성해라.

## 2. Current Market Structure
Python 해석값의 structure_text를 바탕으로 작성해라.

## 3. Key Levels
Python 해석값의 key_levels를 바탕으로 참고 저항 구간과 참고 지지 구간을 설명해라.

## 4. Futures Positioning
Python 해석값의 funding_text, oi_text, positioning_text를 바탕으로 작성해라.

## 5. Long Scenario
Python 해석값의 long_text를 바탕으로 작성해라.

## 6. Short Scenario
Python 해석값의 short_text를 바탕으로 작성해라.

## 7. Risk & Invalidation
### Risk Level
Python 해석값의 risk_text를 바탕으로 작성해라.

### Long Invalidation
Python 해석값의 invalidation.long_invalidation만 사용해서 작성해라.

### Short Invalidation
Python 해석값의 invalidation.short_invalidation만 사용해서 작성해라.

## 8. Trading Plan
아래 3개 항목으로만 작성해라.
절대로 Invalidation 내용을 쓰지 마라.

### 상방 대응
Python 해석값의 trading_plan.upside_plan만 사용해서 작성해라.

### 하방 대응
Python 해석값의 trading_plan.downside_plan만 사용해서 작성해라.

### 대기 조건
Python 해석값의 trading_plan.wait_plan만 사용해서 작성해라.

## 9. Key Checkpoints
Python 해석값의 checkpoint_text를 바탕으로 bullet로 작성해라.
"""
        return prompt.strip()
