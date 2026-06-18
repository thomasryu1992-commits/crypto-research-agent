import os
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv


load_dotenv()


def is_telegram_enabled() -> bool:
    value = os.getenv("TELEGRAM_ENABLED", "false").lower().strip()
    return value in ["true", "1", "yes", "y"]


def get_telegram_config():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN 값이 .env에 없습니다.")

    if not chat_id:
        raise ValueError("TELEGRAM_CHAT_ID 값이 .env에 없습니다.")

    return bot_token, chat_id


def split_message(text: str, max_length: int = 3900):
    """
    Telegram message length 제한을 피하기 위해 긴 메시지를 나눈다.
    4096자 제한보다 약간 낮게 3900자로 자른다.
    """
    if len(text) <= max_length:
        return [text]

    chunks = []
    current = ""

    for line in text.splitlines():
        if len(current) + len(line) + 1 > max_length:
            chunks.append(current)
            current = line
        else:
            current += "\n" + line if current else line

    if current:
        chunks.append(current)

    return chunks


def send_telegram_message(text: str, parse_mode: Optional[str] = None):
    """
    Telegram으로 텍스트 메시지를 전송한다.
    parse_mode는 기본 None으로 둔다.
    Markdown 파싱 에러를 피하기 위해 처음에는 plain text가 안전하다.
    """
    if not is_telegram_enabled():
        return {
            "enabled": False,
            "sent": False,
            "message": "Telegram sending is disabled.",
        }

    bot_token, chat_id = get_telegram_config()

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    chunks = split_message(text)
    responses = []

    for chunk in chunks:
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "disable_web_page_preview": True,
        }

        if parse_mode:
            payload["parse_mode"] = parse_mode

        response = requests.post(url, json=payload, timeout=20)

        if not response.ok:
            raise RuntimeError(
                f"Telegram send failed. status={response.status_code}, response={response.text}"
            )

        responses.append(response.json())

    return {
        "enabled": True,
        "sent": True,
        "chunks": len(chunks),
        "responses": responses,
    }


def send_telegram_report(report_path: Path):
    """
    telegram summary txt 파일을 읽어서 Telegram으로 전송한다.
    """
    report_path = Path(report_path)

    if not report_path.exists():
        raise FileNotFoundError(f"Telegram report file not found: {report_path}")

    text = report_path.read_text(encoding="utf-8")

    if not text.strip():
        raise ValueError(f"Telegram report file is empty: {report_path}")

    return send_telegram_message(text)