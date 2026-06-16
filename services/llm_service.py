from openai import OpenAI
from config import OPENAI_API_KEY


def ask_llm(prompt: str) -> str:
    if not OPENAI_API_KEY:
        return """
OpenAI API key is missing.

.env 파일에 아래 값을 추가해줘.

OPENAI_API_KEY=your_openai_api_key

현재는 LLM 리포트를 생성할 수 없기 때문에, 시장 데이터 수집 구조만 테스트된 상태야.
""".strip()

    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "너는 크립토 시장을 분석하는 전문 리서치 애널리스트다. 데이터 기반으로 차분하고 명확하게 분석한다.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content
