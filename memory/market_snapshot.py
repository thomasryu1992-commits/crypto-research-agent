import json
from datetime import datetime
from pathlib import Path
SNAPSHOT_DIR=Path("data/snapshots")
def save_market_snapshot(symbol:str,snapshot:dict)->str:
    SNAPSHOT_DIR.mkdir(parents=True,exist_ok=True); now=datetime.now().strftime('%Y-%m-%d_%H-%M-%S'); safe=symbol.replace('/','_').replace(':','_'); p=SNAPSHOT_DIR/f"{safe}_{now}_snapshot.json"; p.write_text(json.dumps({"saved_at":now,"symbol":symbol,"snapshot":snapshot},ensure_ascii=False,indent=2),encoding="utf-8"); return str(p)
def load_latest_snapshot(symbol:str)->dict|None:
    if not SNAPSHOT_DIR.exists(): return None
    safe=symbol.replace('/','_').replace(':','_'); files=sorted(SNAPSHOT_DIR.glob(f"{safe}_*_snapshot.json"))
    if not files: return None
    try: return json.loads(files[-1].read_text(encoding="utf-8")).get("snapshot")
    except: return None
