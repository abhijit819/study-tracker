import hashlib
import json
import os
from datetime import datetime

from config import ARCHIVE_MANIFEST


def _load():
    if not ARCHIVE_MANIFEST.exists():
        return {}
    with ARCHIVE_MANIFEST.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("Archive manifest must contain a JSON object")
    return data


def _save(data):
    ARCHIVE_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    temp = ARCHIVE_MANIFEST.with_suffix(".json.tmp")
    with temp.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, sort_keys=True)
        file.flush()
        os.fsync(file.fileno())
    os.replace(temp, ARCHIVE_MANIFEST)


def get_month_state(month_key: str):
    return _load().get(month_key, {}).get("state", "active")


def set_archiving(month_key: str, summary_name: str, checksum: str):
    data = _load()
    data[month_key] = {
        "state": "archiving",
        "summary_file": summary_name,
        "sha256": checksum,
        "archiving_started_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    _save(data)


def set_archived(month_key: str):
    data = _load()
    data[month_key]["state"] = "archived"
    data[month_key]["archived_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    _save(data)


def get_all_entries():
    return _load()


def checksum_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_archiving_summary(month_key: str, path):
    entry = _load().get(month_key)
    return bool(
        entry
        and entry.get("state") in {"archiving", "archived"}
        and path.exists()
        and checksum_file(path) == entry.get("sha256")
    )
