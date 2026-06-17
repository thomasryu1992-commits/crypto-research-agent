from datetime import datetime
from pathlib import Path
REPORT_DIR=Path("data/reports")
def save_report(report:str)->str:
    REPORT_DIR.mkdir(parents=True,exist_ok=True); p=REPORT_DIR/f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_daily_report.txt"; p.write_text(report,encoding="utf-8"); return str(p)
def load_latest_report()->str|None:
    files=sorted(REPORT_DIR.glob("*_daily_report.txt")) if REPORT_DIR.exists() else []
    return files[-1].read_text(encoding="utf-8") if files else None
