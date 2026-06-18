from datetime import datetime
from pathlib import Path


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def build_file_stem(timeframe: str, suffix: str, calibrated_suffix: str, context_suffix: str):
    return f"btc_{timeframe}_{suffix}{calibrated_suffix}{context_suffix}_latest_report"


def convert_txt_to_markdown(report: str) -> str:
    """
    현재 report_builder가 텍스트 중심으로 생성하더라도
    markdown 파일에서 읽기 좋게 그대로 보존한다.
    """
    return report.strip() + "\n"


def build_telegram_summary(final_report: str, max_chars: int = 3500) -> str:
    """
    Telegram 전송용 짧은 요약본 생성.
    지금은 rule-based 압축 버전이고, 다음 단계에서 실제 Telegram 전송을 붙인다.
    """
    lines = final_report.splitlines()

    important_keywords = [
        "Market State",
        "Market Score",
        "Market Bias",
        "Overlay Status",
        "Conviction Level",
        "Main Risk",
        "Best Research Action",
        "Final Conclusion",
        "Risk Flags",
        "BTC Price",
        "24H Price Change",
        "Funding Rate",
        "Open Interest",
        "Long/Short Ratio",
        "24H Liquidation",
    ]

    selected_lines = []

    for line in lines:
        clean_line = line.strip()

        if not clean_line:
            continue

        if clean_line.startswith("#"):
            selected_lines.append(clean_line)
            continue

        if any(keyword in clean_line for keyword in important_keywords):
            selected_lines.append(clean_line)

    if not selected_lines:
        selected_lines = lines[:40]

    telegram_text = "\n".join(selected_lines)

    if len(telegram_text) > max_chars:
        telegram_text = telegram_text[:max_chars] + "\n\n... [truncated]"

    return telegram_text


def save_report_outputs(
    final_report: str,
    report_dir: Path,
    timeframe: str,
    suffix: str,
    calibrated_suffix: str,
    context_suffix: str,
):
    """
    리포트를 latest / archive / telegram summary 형태로 저장한다.
    """
    ensure_dir(report_dir)

    archive_dir = report_dir / "archive"
    telegram_dir = report_dir / "telegram"

    ensure_dir(archive_dir)
    ensure_dir(telegram_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    file_stem = build_file_stem(
        timeframe=timeframe,
        suffix=suffix,
        calibrated_suffix=calibrated_suffix,
        context_suffix=context_suffix,
    )

    latest_txt_path = report_dir / f"{file_stem}.txt"
    latest_md_path = report_dir / f"{file_stem}.md"

    archive_txt_path = archive_dir / f"{file_stem}_{timestamp}.txt"
    archive_md_path = archive_dir / f"{file_stem}_{timestamp}.md"

    latest_simple_md_path = report_dir / f"latest_btc_{timeframe}_report.md"
    latest_simple_txt_path = report_dir / f"latest_btc_{timeframe}_report.txt"

    telegram_summary_path = telegram_dir / f"latest_btc_{timeframe}_telegram.txt"

    markdown_report = convert_txt_to_markdown(final_report)
    telegram_summary = build_telegram_summary(final_report)

    latest_txt_path.write_text(final_report, encoding="utf-8")
    latest_md_path.write_text(markdown_report, encoding="utf-8")

    archive_txt_path.write_text(final_report, encoding="utf-8")
    archive_md_path.write_text(markdown_report, encoding="utf-8")

    latest_simple_md_path.write_text(markdown_report, encoding="utf-8")
    latest_simple_txt_path.write_text(final_report, encoding="utf-8")

    telegram_summary_path.write_text(telegram_summary, encoding="utf-8")

    return {
        "latest_txt_path": latest_txt_path,
        "latest_md_path": latest_md_path,
        "archive_txt_path": archive_txt_path,
        "archive_md_path": archive_md_path,
        "latest_simple_md_path": latest_simple_md_path,
        "latest_simple_txt_path": latest_simple_txt_path,
        "telegram_summary_path": telegram_summary_path,
    }