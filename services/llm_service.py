import requests
from config import OLLAMA_BASE_URL, OLLAMA_MODEL


def ask_llm(prompt: str) -> str:
    url = f"{OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_ctx": 8192,
            "num_predict": 4096,
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=(30, 600))
        response.raise_for_status()

        data = response.json()
        result = data.get("response", "").strip()

        if not result:
            return "Ollama 응답이 비어 있습니다. 모델명과 Ollama 실행 상태를 확인해야 합니다."

        return result

    except requests.exceptions.ConnectTimeout:
        return "Ollama 연결 시간이 초과되었습니다. Ollama가 실행 중인지 확인해줘."

    except requests.exceptions.ReadTimeout:
        return (
            "Ollama 응답 시간이 초과되었습니다. "
            "모델이 너무 느리거나 프롬프트가 길 수 있습니다. "
            "gemma3:1b 같은 더 작은 모델로 테스트해보는 것이 좋습니다."
        )

    except requests.exceptions.ConnectionError:
        return f"Ollama에 연결할 수 없습니다. 터미널에서 `ollama run {OLLAMA_MODEL}`로 모델 실행을 확인해줘."

    except requests.RequestException as e:
        return f"Ollama 호출에 실패했습니다. 에러: {e}"
