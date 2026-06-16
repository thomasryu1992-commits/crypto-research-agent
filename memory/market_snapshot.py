import json
from datetime import datetime
from pathlib import Path

SNAPSHOT_DIR = Path("data/snapshots")


def save_market_snapshot(symbol: str, snapshot: dict) -> str:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_symbol = symbol.replace("/", "_").replace(":", "_")
    file_path = SNAPSHOT_DIR / f"{safe_symbol}_{now}_snapshot.json"

    payload = {"saved_at": now, "symbol": symbol, "snapshot": snapshot}
    file_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(file_path)


def load_latest_snapshot(symbol: str) -> dict | None:
    if not SNAPSHOT_DIR.exists():
        return None

    safe_symbol = symbol.replace("/", "_").replace(":", "_")
    files = sorted(SNAPSHOT_DIR.glob(f"{safe_symbol}_*_snapshot.json"))
    if not files:
        return None

    latest_file = files[-1]
    try:
        payload = json.loads(latest_file.read_text(encoding="utf-8"))
        return payload.get("snapshot")
    except (json.JSONDecodeError, OSError):
        return None
