import csv
import json
from pathlib import Path


def write_csv(path: str | Path, rows: list[dict]):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fieldnames = _flatten_keys(rows)

    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(_flatten_row(row))


def write_json(path: str | Path, data: dict):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _flatten_keys(rows):
    keys = []
    seen = set()

    for row in rows:
        flat = _flatten_row(row)
        for k in flat.keys():
            if k not in seen:
                seen.add(k)
                keys.append(k)

    return keys


def _flatten_row(row, prefix=""):
    flat = {}

    for key, value in row.items():
        name = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):
            flat.update(_flatten_row(value, name))
        else:
            flat[name] = value

    return flat
