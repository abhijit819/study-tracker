import csv
import json
import os

from config import SUBJECT_METADATA, DAILY_LOG_DIR, MONTHLY_SUMMARY_DIR


def _unique(names):
    result, seen = [], set()
    for value in names:
        if not isinstance(value, str):
            continue
        name = value.strip()
        key = name.casefold()
        if name and key not in seen:
            seen.add(key)
            result.append(name)
    return result


def _discover(directory):
    names = []
    if not directory.exists():
        return names
    for path in sorted(directory.glob("*.csv")):
        try:
            with path.open("r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                if reader.fieldnames and "subject" in reader.fieldnames:
                    names.extend(row.get("subject", "") for row in reader)
        except (OSError, UnicodeError, csv.Error):
            # Discovery is best-effort; normal data readers perform validation.
            continue
    return names


def load_subject_metadata():
    data = {}
    if SUBJECT_METADATA.exists():
        with SUBJECT_METADATA.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise ValueError("Subject metadata must contain a JSON object")

    subjects = _unique(
        list(data.get("subjects", []))
        + _discover(DAILY_LOG_DIR)
        + _discover(MONTHLY_SUMMARY_DIR)
    )
    current = data.get("current_subject", "")
    current = current.strip() if isinstance(current, str) else ""
    if current:
        current = next((s for s in subjects if s.casefold() == current.casefold()), current)
        if current.casefold() not in {s.casefold() for s in subjects}:
            subjects.append(current)
    else:
        current = subjects[0] if subjects else "System Design"
        if current.casefold() not in {s.casefold() for s in subjects}:
            subjects.append(current)
    return {"subjects": subjects, "current_subject": current}


def canonical_subject(name, subjects):
    name = name.strip()
    if not name:
        raise ValueError("Subject cannot be empty")
    key = name.casefold()
    for existing in subjects:
        if existing.casefold() == key:
            return existing
    subjects.append(name)
    return name


def save_subject_metadata(subjects, current_subject):
    data = {
        "version": 1,
        "subjects": _unique(subjects),
        "current_subject": current_subject.strip(),
    }
    SUBJECT_METADATA.parent.mkdir(parents=True, exist_ok=True)
    temp = SUBJECT_METADATA.with_suffix(".json.tmp")
    with temp.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.flush()
        os.fsync(file.fileno())
    os.replace(temp, SUBJECT_METADATA)
