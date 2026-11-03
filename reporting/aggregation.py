from collections import defaultdict
from datetime import date, timedelta

from storage.monthly_summaries import summary_path, validate_month_summary


def _months_between(start: date, end: date):
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        yield year, month
        if month == 12:
            year, month = year + 1, 1
        else:
            month += 1


def _quarter_label(day: date):
    return f"{day.year}-Q{((day.month - 1) // 3) + 1}"


def get_study_data(start_date: date, end_date: date, granularity="day", subject=None):
    # Return (period labels, subject names, series) for day/month/quarter/year.
    if end_date < start_date:
        raise ValueError("End date must not be earlier than start date")
    if granularity not in {"day", "month", "quarter", "year"}:
        raise ValueError("Unsupported granularity")

    daily = defaultdict(int)
    subjects = set()
    for year, month in _months_between(start_date, end_date):
        path = summary_path(year, month)
        if not path.exists():
            continue
        for row in validate_month_summary(year, month):
            day = date.fromisoformat(row["date"])
            name = row["subject"]
            if start_date <= day <= end_date and (subject is None or name == subject):
                subjects.add(name)
                daily[(day, name)] += int(row["duration_minutes"])

    if subject is not None:
        subjects.add(subject)

    if granularity == "day":
        labels, cursor = [], start_date
        while cursor <= end_date:
            labels.append(cursor.isoformat())
            cursor += timedelta(days=1)
        bucket = lambda d: d.isoformat()
    elif granularity == "month":
        labels = [f"{y:04d}-{m:02d}" for y, m in _months_between(start_date, end_date)]
        bucket = lambda d: f"{d.year:04d}-{d.month:02d}"
    elif granularity == "quarter":
        labels = []
        cursor = date(start_date.year, ((start_date.month - 1) // 3) * 3 + 1, 1)
        while cursor <= end_date:
            labels.append(_quarter_label(cursor))
            m = cursor.month + 3
            cursor = date(cursor.year + (m - 1) // 12, (m - 1) % 12 + 1, 1)
        bucket = _quarter_label
    else:
        labels = [str(y) for y in range(start_date.year, end_date.year + 1)]
        bucket = lambda d: str(d.year)

    series = {name: [0] * len(labels) for name in sorted(subjects)}
    indexes = {label: i for i, label in enumerate(labels)}
    for (day, name), minutes in daily.items():
        label = bucket(day)
        if label in indexes:
            series[name][indexes[label]] += minutes
    return labels, sorted(subjects), series
