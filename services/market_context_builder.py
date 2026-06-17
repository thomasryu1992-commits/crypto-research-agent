def build_market_context(snapshot:dict,delta:dict,previous_snapshot:dict|None)->dict:
    pc=snapshot.get("price_change_percent_24h")
    fr=snapshot.get("funding_rate")
    oi=delta.get("open_interest_change_since_last_snapshot")
    trend=snapshot.get("candle_summary",{}).get("trend")
    bias=_bias(pc,fr,oi,trend)
    pos=_positioning(pc,fr,oi)
    risk=_risk(pc,fr,oi)
    return {"bias":bias,"positioning_structure":pos,"risk_level":risk,"chasing_allowed":False,"recommended_mode":"confirmation_required","language_policy":_language_policy(),"long_setup":_long_setup(pos,bias,trend),"short_setup":_short_setup(pos,bias,trend),"invalidation_rules":_invalidation(),"notes_for_llm":["직접적인 진입/청산 명령을 쓰지 마라.","상방/하방 대응은 시나리오 강화로 표현해라.","OI는 항상 시장 전체 OI라고 표현해라."]}

def _bias(pc,fr,oi,trend):
    if pc is None or fr is None: return "neutral"
    if pc>1 and trend=="uptrend": return "neutral_to_bullish" if fr<0 else "mildly_bullish"
    if pc<-1 and trend=="downtrend": return "bearish_with_short_build_up" if fr<0 and oi is not None and oi>1 else "mildly_bearish"
    return "neutral"

def _positioning(pc,fr,oi):
    if pc is None or fr is None: return "insufficient_data"
    oi_up=oi is not None and oi>0.2
    oi_down=oi is not None and oi<-0.2
    if pc>0 and fr<0 and (oi_up or oi is None): return "price_up_funding_negative_oi_up_short_pressure"
    if pc>0 and fr>0 and oi_up: return "price_up_funding_positive_oi_up_long_overheat_risk"
    if pc<0 and fr<0 and oi_up: return "price_down_funding_negative_oi_up_short_dominant"
    if pc<0 and fr>0 and oi_up: return "price_down_funding_positive_oi_up_long_trap_risk"
    if pc>0 and oi_down: return "price_up_oi_down_short_covering_possible"
    if pc<0 and oi_down: return "price_down_oi_down_deleveraging"
    return "mixed_or_range_positioning"

def _risk(pc,fr,oi):
    if pc is None or fr is None: return "Medium"
    if abs(pc)>=3 or (oi is not None and abs(oi)>=5): return "High"
    if abs(pc)>=1 or abs(fr)>0.0001 or (oi is not None and abs(oi)>=1): return "Medium"
    return "Low"

def _long_setup(pos,bias,trend):
    if "short_pressure" in pos: thesis="가격 상승, 음수 Funding, 시장 전체 OI 유지/증가 조합은 숏 포지션 압박 구조일 수 있습니다."
    elif "overheat" in pos: thesis="롱 유입은 강하지만 과열 리스크가 있어 돌파 추격보다 리테스트 확인이 필요합니다."
    elif trend=="downtrend": thesis="현재 흐름이 약하기 때문에 상방 시나리오는 단기 저항 회복과 1H 종가 유지가 확인될 때만 강화됩니다."
    else: thesis="상방 시나리오는 직전 고점 돌파와 1H 종가 유지가 확인될 때만 강화됩니다."
    return {"thesis":thesis,"valid_conditions":["직전 고점 또는 단기 저항 돌파","1H 종가가 돌파 구간 위에서 마감","시장 전체 OI 유지 또는 증가","Funding Rate 음수 또는 중립 유지","가격 상승 시 거래량 동반"],"banned_wording":["롱 포지션을 진입합니다","롱 포지션을 강화합니다","추격 진입이 유리합니다"]}

def _short_setup(pos,bias,trend):
    if "short_dominant" in pos: thesis="가격 하락, 음수 Funding, 시장 전체 OI 증가 조합은 신규 숏 유입 또는 숏 우위 추세일 수 있습니다."
    elif "long_trap" in pos: thesis="가격 하락, 양수 Funding, 시장 전체 OI 증가 조합은 롱 포지션이 갇히는 구조일 수 있습니다."
    else: thesis="하방 시나리오는 단기 지지 이탈과 회복 실패가 확인될 때만 강화됩니다."
    return {"thesis":thesis,"valid_conditions":["단기 지지 구간 또는 현재 가격대 하단 이탈","1H 종가가 이탈 구간 아래에서 마감","반등 시 이전 지지 구간 회복 실패","하락 중 시장 전체 OI 유지 또는 증가","반등 시 거래량 부족"],"banned_wording":["숏 포지션을 진입합니다","숏 포지션을 청산합니다","숏 커버링 필요"]}

def _invalidation():
    return {"long_invalidation":["가격의 1H 종가가 돌파 구간 위에서 유지되지 못함","단기 지지 구간 이탈","가격 하락과 함께 시장 전체 OI 증가"],"short_invalidation":["가격이 직전 고점 또는 단기 저항을 강하게 돌파","가격의 1H 종가가 저항 위에서 유지","시장 전체 OI 유지 또는 증가와 함께 가격 상승"]}

def _language_policy():
    return {"must_use":["상방 시나리오가 강화됩니다","하방 시나리오가 강화됩니다","시장 전체 OI"],"banned_phrases":["롱 포지션을 진입합니다","숏 포지션을 진입합니다","숏 포지션을 청산합니다","롱 포지션의 OI","숏 포지션의 OI","추격 진입이 유리합니다"]}
