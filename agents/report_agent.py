from services.llm_service import ask_llm
from tools.telegram_tool import send_telegram_message
from memory.report_memory import save_report
from config import REPORT_LANGUAGE, SEND_TELEGRAM


class ReportAgent:
    def generate_report(self, market_data: dict) -> str:
        prompt = self._build_prompt(market_data)
        report = ask_llm(prompt)

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

    def _build_prompt(self, market_data: dict) -> str:
        language_instruction = "한국어로 작성해줘." if REPORT_LANGUAGE == "ko" else "Write in English."

        return f"""
너는 크립토 선물 시장을 분석하는 트레이딩 리서치 애널리스트야.

이번 리포트에서는 네가 모든 판단을 새로 만들지 않는다.
Python rule engine이 먼저 계산한 `market_context`를 최우선 기준으로 사용한다.

작성 언어:
{language_instruction}

가장 중요한 목표:
이 리포트는 단순 시장 요약이 아니라, 실제 트레이딩 의사결정에 참고할 수 있는 조건부 시나리오 리포트여야 한다.

최우선 규칙:
- market_context의 판단을 거스르지 마라.
- market_context.chasing_allowed가 False이면 절대 "추격 진입이 유리하다"고 쓰지 마라.
- market_context.recommended_mode가 confirmation_required이면 "확인 매매", "돌파 확인", "리테스트 확인", "조건부 대응" 중심으로 작성해라.
- market_context.long_setup.do_not_say에 포함된 표현을 사용하지 마라.
- market_context.short_setup.do_not_say에 포함된 표현을 사용하지 마라.
- Short Scenario 섹션에서는 "숏 청산", "숏 커버링", "포지션 종료"라는 표현을 절대 쓰지 마라.
- Long Scenario 섹션에서는 "롱 청산", "포지션 종료"라는 표현을 쓰지 마라.
- 포지션 종료나 무효화는 Invalidation 섹션에서만 다룬다.

기본 작성 원칙:
- 단정적인 매수/매도 지시는 하지 않는다.
- "지금 롱", "지금 숏", "매수하라", "매도하라" 같은 명령문을 쓰지 않는다.
- 조건이 충족되면 어떤 시나리오가 강화되는지 설명한다.
- 가격, Funding Rate, Open Interest, 캔들 흐름을 연결해서 해석한다.
- Funding Rate만 보고 숏 스퀴즈를 단정하지 않는다.
- Open Interest만 보고 방향성을 단정하지 않는다.
- 변화율 데이터가 있으면 절대값보다 변화율을 우선적으로 해석한다.
- 알 수 없는 지지선/저항선 가격을 임의로 만들지 않는다.
- 가격 레벨을 알 수 없으면 "직전 고점", "단기 저항", "현재 가격대", "주요 지지 구간", "단기 지지선"처럼 표현한다.
- "오묘하게", "추가 분석이 필요합니다", "가능성이 있습니다" 같은 모호한 표현을 피한다.
- 각 시나리오는 조건 → 해석 → 관찰 포인트 순서로 작성한다.
- 서로 충돌하는 문장을 쓰지 않는다.

리포트 형식:

# Daily BTC Trading Research Report

## 1. Market Bias
market_context.bias를 기준으로 현재 시장 방향성을 분류해.
가능한 표현:
- neutral = 중립
- neutral_to_bullish = 중립 ~ 약상방
- mildly_bullish = 약상방
- bullish_but_overheated = 약상방이지만 과열 주의
- neutral_to_bearish_with_long_trap_risk = 중립 ~ 약하방, 롱 트랩 리스크
- bearish_with_short_build_up = 약하방, 숏 우위
- mildly_bearish = 약하방

반드시 포함:
- Bias 판단
- 판단 근거
- 가격, Funding, OI, 캔들 흐름 조합
- 현재가 추격 구간인지 확인 구간인지

## 2. Current Market Structure
현재 가격 구조를 설명해.

반드시 포함:
- 현재 가격
- 24시간 가격 변화율
- 24시간 고가/저가가 있으면 활용
- 최근 1시간봉 캔들 요약
- 상승 추세 / 하락 추세 / 박스권 여부
- 추격 진입이 아니라 확인이 필요한 이유

중요:
market_context.chasing_allowed가 False이면 반드시 "현재는 추격 진입보다 확인이 필요한 구간"이라고 써라.

## 3. Futures Positioning
Funding Rate와 Open Interest를 함께 해석해.

반드시 포함:
- Funding Rate 양수/음수/중립
- OI의 이전 스냅샷 대비 변화율
- 가격 변화와 OI 변화의 조합
- market_context.positioning_structure 해석
- 숏 압박 / 롱 과열 / 롱 트랩 / 숏 우위 / 디레버리징 중 어디에 가까운지

## 4. Long Scenario
market_context.long_setup을 기준으로 작성해.

반드시 아래 구조로 작성:

### 유효 조건
market_context.long_setup.valid_conditions를 자연스럽게 풀어서 설명해.

### 해석
market_context.long_setup.thesis를 기준으로 설명해.

### 관찰 포인트
롱 시나리오를 보기 전에 확인해야 할 데이터:
- 직전 고점 또는 단기 저항 돌파
- 1H 종가 유지
- OI 유지 또는 증가
- Funding Rate 음수 또는 중립 유지
- 거래량 동반

### 주의할 점
추격 진입을 피해야 하는 이유를 설명해.
직접적인 매수 지시는 하지 마라.

## 5. Short Scenario
market_context.short_setup을 기준으로 작성해.

반드시 아래 구조로 작성:

### 유효 조건
market_context.short_setup.valid_conditions를 자연스럽게 풀어서 설명해.

### 해석
market_context.short_setup.thesis를 기준으로 설명해.

### 관찰 포인트
숏 시나리오를 보기 전에 확인해야 할 데이터:
- 단기 지지 구간 또는 현재 가격대 하단 이탈
- 1H 종가가 이탈 구간 아래에서 마감
- 반등 시 이전 지지 구간 회복 실패
- 하락 중 OI 유지 또는 증가
- 반등 시 거래량 부족

### 주의할 점
하락 이후 과도한 추격 숏이 위험한 이유를 설명해.
직접적인 매도 지시는 하지 마라.

절대 금지:
이 섹션에서는 "숏 청산", "숏 커버링", "포지션 종료"라는 표현을 쓰지 마라.

## 6. Invalidation
market_context.invalidation_rules를 기준으로 작성해.

반드시 포함:
### Long Invalidation
롱 시나리오가 약해지는 조건을 설명해.

### Short Invalidation
숏 시나리오가 약해지는 조건을 설명해.

## 7. Risk Level
market_context.risk_level을 기준으로 Low / Medium / High 중 하나로 분류해.

반드시 포함:
- 리스크 등급
- 리스크 판단 근거
- 변동성이 커질 수 있는 조건
- 현재 가장 조심해야 할 행동

중요:
"변동성을 관찰하고 예측한다"처럼 추상적으로 쓰지 마라.
구체적으로 "확인 없는 추격 진입", "지지/저항 근처에서의 늦은 진입", "OI 급증 구간에서의 과도한 레버리지"처럼 써라.

## 8. Trading Plan
직접적인 매수/매도 지시가 아니라 조건부 대응 계획으로 작성해.

### 상방 대응 계획
- 저항 돌파
- 1H 종가 유지
- OI 유지/증가
- Funding 음수 또는 중립 유지
- 거래량 동반

### 하방 대응 계획
- 단기 지지 이탈
- 1H 종가가 이탈 구간 아래에서 마감
- 반등 시 이전 지지 회복 실패
- 하락 중 OI 유지/증가
- 거래량 부족

### 대기 조건
- 가격이 저항과 지지 사이에 머무르는 경우
- OI와 Funding이 뚜렷한 방향성을 보이지 않는 경우
- 캔들이 박스권에 머무르는 경우

중요:
하방 대응 계획에서 "1H 종가가 저항 위에서 유지"라는 표현은 절대 쓰지 마라.
하방 대응 계획에서는 "이탈 구간 아래에서 마감" 또는 "이전 지지 회복 실패"라고 써라.

## 9. Key Checkpoints
오늘 체크해야 할 핵심 포인트를 bullet로 정리해.

반드시 포함:
- 직전 고점 또는 단기 저항 돌파 여부
- 1H 종가 기준 돌파 유지 여부
- 단기 지지 구간 이탈 여부
- 1H 종가가 이탈 구간 아래에서 마감하는지
- Funding Rate 방향
- OI 증가/감소 여부
- 가격 상승/하락 시 거래량 동반 여부
- 이전 스냅샷 대비 변화율
- 현재 구간이 추격 구간인지 확인 구간인지

시장 데이터:
{market_data}
""".strip()
