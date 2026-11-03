from datetime import date

from storage.archive_registry import (
    checksum_file, get_all_entries, get_month_state, set_archived,
    set_archiving, verify_archiving_summary,
)
from storage.daily_logs import delete_month_logs, list_daily_log_paths
from storage.monthly_summaries import summary_path, validate_month_summary
from services.summary_service import month_key, rebuild_month_summary


def _finish_archive(year: int, month: int, key: str):
    path = summary_path(year, month)
    if not verify_archiving_summary(key, path):
        raise ValueError("Monthly summary is missing or its archive checksum does not match")
    path.chmod(0o444)
    delete_month_logs(year, month)
    set_archived(key)


def archive_month(year: int, month: int):
    today = date.today()
    if (year, month) >= (today.year, today.month):
        raise ValueError("Only completed months can be archived")

    key = month_key(year, month)
    state = get_month_state(key)
    if state == "archived":
        raise PermissionError(f"{key} is already archived")
    if state == "archiving":
        _finish_archive(year, month, key)
        return {}, "Resumed and completed the interrupted archive."

    path = summary_path(year, month)
    logs = list_daily_log_paths(year, month)
    rebuild_error = None

    # Never overwrite an existing summary with an empty rebuild if no logs remain.
    if logs:
        try:
            rebuild_month_summary(year, month)
            validate_month_summary(year, month)
            source = "rebuilt from daily logs"
        except Exception as exc:
            rebuild_error = exc
            try:
                validate_month_summary(year, month)
                source = "existing monthly summary (daily logs were unusable)"
            except Exception as summary_exc:
                raise RuntimeError(
                    "Cannot archive: logs could not rebuild the summary and the "
                    "existing summary is invalid. Daily logs were retained."
                ) from summary_exc
    else:
        try:
            validate_month_summary(year, month)
            source = "existing monthly summary (no daily logs found)"
        except Exception as exc:
            raise RuntimeError(
                "Cannot archive: no daily logs and no valid monthly summary."
            ) from exc

    totals = {}
    for row in validate_month_summary(year, month):
        totals[row["subject"]] = totals.get(row["subject"], 0) + int(row["duration_minutes"])

    set_archiving(key, path.name, checksum_file(path))
    _finish_archive(year, month, key)

    message = f"Archived using the {source}."
    if rebuild_error:
        message += f" Rebuild error: {rebuild_error}"
    return totals, message


def resume_interrupted_archives():
    messages = []
    for key, entry in get_all_entries().items():
        if entry.get("state") == "archiving":
            try:
                year, month = map(int, key.split("-"))
                _finish_archive(year, month, key)
                messages.append(f"Completed interrupted archive for {key}.")
            except Exception as exc:
                messages.append(f"Could not resume archive for {key}: {exc}")
    return messages
