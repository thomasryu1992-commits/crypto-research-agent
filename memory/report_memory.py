from datetime import datetime
from pathlib import Path

REPORT_DIR = Path("data/reports")


def save_report(report: str) -> str:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = REPORT_DIR / f"{now}_daily_report.txt"
    file_path.write_text(report, encoding="utf-8")
    return str(file_path)


def load_latest_report() -> str | None:
    if not REPORT_DIR.exists():
        return None
    files = sorted(REPORT_DIR.glob("*_daily_report.txt"))
    if not files:
        return None
    return files[-1].read_text(encoding="utf-8")
