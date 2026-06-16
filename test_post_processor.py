from services.report_post_processor import clean_report_language

sample = """
저항 돌파 시, 롱 포지션을 진입합니다.
단기 지지 이탈 시, 숏 포지션을 청산합니다.
7개의 밀리미터 상승 캔들과 17개의 밀리미터 하락 캔들
롱 포지션의 OI
숏 포지션의 OI
"""

result = clean_report_language(sample)

print(result)