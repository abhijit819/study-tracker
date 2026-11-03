from datetime import date

from config import MONTHLY_SUMMARY_DIR, SUMMARY_FIELDS
from storage.csv_utils import atomic_write_csv, read_csv_with_header


def summary_path(year: int, month: int):
    return MONTHLY_SUMMARY_DIR / f"{year:04d}-{month:02d}.csv"


def read_month_summary(year: int, month: int):
    path = summary_path(year, month)
    if not path.exists():
        raise FileNotFoundError(path)
    header, rows = read_csv_with_header(path)
    if header != SUMMARY_FIELDS:
        raise ValueError(f"Invalid summary header in {path.name}")
    return rows


def write_month_summary(year: int, month: int, totals):
    rows = [
        {"date": day, "subject": subject, "duration_minutes": minutes}
        for (day, subject), minutes in sorted(totals.items())
    ]
    atomic_write_csv(summary_path(year, month), SUMMARY_FIELDS, rows)


def validate_month_summary(year: int, month: int):
    rows = read_month_summary(year, month)
    seen = set()
    for row in rows:
        try:
            day = date.fromisoformat(row["date"])
            minutes = int(row["duration_minutes"])
            subject = row["subject"].strip()
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Summary contains an invalid date, subject, or duration") from exc
        if day.year != year or day.month != month:
            raise ValueError("Summary contains a date outside its month")
        if not subject or minutes < 0:
            raise ValueError("Summary contains an empty subject or negative duration")
        key = (row["date"], subject)
        if key in seen:
            raise ValueError("Summary contains duplicate date/subject rows")
        seen.add(key)
    return rows
