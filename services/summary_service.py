import calendar
from collections import defaultdict
from datetime import date, timedelta

from storage.archive_registry import get_month_state
from storage.daily_logs import list_daily_log_paths, read_daily_log
from storage.monthly_summaries import summary_path, validate_month_summary, write_month_summary


def month_key(year: int, month: int):
    return f"{year:04d}-{month:02d}"


def _month_end(year: int, month: int):
    return date(year, month, calendar.monthrange(year, month)[1])


def _complete_daily_rows(totals, year: int, month: int):
    if not totals:
        return totals
    subjects = sorted({subject for _, subject in totals})
    first_dates = {
        subject: min(date.fromisoformat(day) for day, name in totals if name == subject)
        for subject in subjects
    }
    today = date.today()
    through = min(_month_end(year, month), today) if (year, month) == (today.year, today.month) else _month_end(year, month)
    completed = dict(totals)
    for subject, first_day in first_dates.items():
        cursor = first_day
        while cursor <= through:
            completed.setdefault((cursor.isoformat(), subject), 0)
            cursor += timedelta(days=1)
    return completed


def update_summary_for_session(subject: str, session_day: date, minutes: int):
    key = month_key(session_day.year, session_day.month)
    if get_month_state(key) != "active":
        raise PermissionError(f"{key} is not active; its summary cannot be changed")

    path = summary_path(session_day.year, session_day.month)
    totals = {}
    if path.exists():
        for row in validate_month_summary(session_day.year, session_day.month):
            totals[(row["date"], row["subject"])] = int(row["duration_minutes"])

    row_key = (session_day.isoformat(), subject)
    totals[row_key] = totals.get(row_key, 0) + minutes
    write_month_summary(
        session_day.year, session_day.month,
        _complete_daily_rows(totals, session_day.year, session_day.month),
    )


def rebuild_month_summary(year: int, month: int):
    key = month_key(year, month)
    if get_month_state(key) != "active":
        raise PermissionError(f"{key} is archived or being archived; rebuild is forbidden")

    totals = defaultdict(int)
    paths = list_daily_log_paths(year, month)
    if not paths:
        raise ValueError(
            f"No daily logs found for {key}; existing summary, if any, was left unchanged."
        )

    for path in paths:
        try:
            file_day = date.fromisoformat(path.stem)
        except ValueError as exc:
            raise ValueError(f"Invalid daily-log filename: {path.name}") from exc

        for row in read_daily_log(path):
            try:
                start_day = date.fromisoformat(row["start_time"][:10])
                minutes = int(row["duration_minutes"])
                subject = row["subject"].strip()
                if start_day != file_day or not subject or minutes < 0:
                    raise ValueError
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Invalid session row in {path.name}") from exc
            totals[(file_day.isoformat(), subject)] += minutes

    write_month_summary(year, month, _complete_daily_rows(dict(totals), year, month))
    return len(paths)


def get_month_totals(year: int, month: int):
    totals = defaultdict(int)
    for row in validate_month_summary(year, month):
        totals[row["subject"]] += int(row["duration_minutes"])
    return dict(totals)


def ensure_current_month_summary_exists():
    today = date.today()
    path = summary_path(today.year, today.month)
    if not path.exists():
        write_month_summary(today.year, today.month, {})
