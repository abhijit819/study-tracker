import csv
from datetime import date

from config import DAILY_FIELDS, DAILY_LOG_DIR
from storage.csv_utils import read_csv_with_header


def daily_log_path(day: date):
    return DAILY_LOG_DIR / f"{day.isoformat()}.csv"


def append_session(day: date, row: dict):
    path = daily_log_path(day)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists() or path.stat().st_size == 0:
        fieldnames = DAILY_FIELDS
        write_header = True
    else:
        fieldnames, _ = read_csv_with_header(path)
        write_header = False
        # Preserve an older file's header layout while appending to it.
        if "duration_seconds" in fieldnames and "duration_minutes" not in fieldnames:
            row = dict(row)
            row["duration_seconds"] = int(row["duration_minutes"]) * 60

    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        writer.writerow(row)
        file.flush()


def list_daily_log_paths(year: int, month: int):
    prefix = f"{year:04d}-{month:02d}-"
    return sorted(p for p in DAILY_LOG_DIR.glob(f"{prefix}*.csv") if p.stem.startswith(prefix))


def read_daily_log(path):
    header, rows = read_csv_with_header(path)
    legacy = {"subject", "start_time", "end_time"}
    current = set(DAILY_FIELDS)
    if not (current.issubset(header) or legacy.issubset(header)):
        raise ValueError(f"{path.name} has an invalid daily-log header")

    normalized = []
    for row in rows:
        if not row.get("subject"):
            raise ValueError(f"{path.name} contains an empty subject")
        if not row.get("duration_minutes") and row.get("duration_seconds") is None:
            raise ValueError(f"{path.name} contains no duration")
        if not row.get("duration_minutes") and row.get("duration_seconds") is not None:
            try:
                row["duration_minutes"] = str(int(round(int(row["duration_seconds"]) / 60)))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{path.name} contains an invalid duration") from exc
        row.setdefault("session_id", "")
        normalized.append(row)
    return normalized


def delete_month_logs(year: int, month: int):
    paths = list_daily_log_paths(year, month)
    for path in paths:
        path.unlink()
    return paths
