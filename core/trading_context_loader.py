import json
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_TRADING_CONTEXT_PATH = (
    Path(__file__).resolve().parents[2]
    / "TradingBot_V33"
    / "data"
    / "exports"
    / "latest_btc_research_context.json"
)


def load_trading_context(path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    TradingBot_V33에서 생성한 latest_btc_research_context.json을 읽는다.
    파일이 없으면 None을 반환해서 기존 Research Agent 실행을 막지 않는다.
    """
    context_path = Path(path) if path else DEFAULT_TRADING_CONTEXT_PATH

    if not context_path.exists():
        return None

    with open(context_path, "r", encoding="utf-8") as file:
        return json.load(file)