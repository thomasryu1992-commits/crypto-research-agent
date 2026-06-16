import requests
from config import OLLAMA_BASE_URL, OLLAMA_MODEL


def ask_llm(prompt: str) -> str:
    url = f"{OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=180)
        response.raise_for_status()

        data = response.json()
        return data.get("response", "").strip()

    except requests.RequestException as e:
        return f"""
Ollama 호출에 실패했습니다.

확인할 것:
1. Ollama가 설치되어 있는지 확인
2. 터미널에서 `ollama --version` 확인
3. 모델이 설치되어 있는지 확인: `ollama list`
4. 모델 다운로드: `ollama pull {OLLAMA_MODEL}`
5. Ollama가 백그라운드에서 실행 중인지 확인

에러:
{e}
""".strip()