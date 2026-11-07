from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DAILY_LOG_DIR = DATA_DIR / "daily_logs"
MONTHLY_SUMMARY_DIR = DATA_DIR / "monthly_summaries"
METADATA_DIR = DATA_DIR / "metadata"
ARCHIVE_MANIFEST = METADATA_DIR / "archives.json"
SUBJECT_METADATA = METADATA_DIR / "subjects.json"

DAILY_FIELDS = ["session_id", "subject", "start_time", "end_time", "duration_minutes"]
SUMMARY_FIELDS = ["date", "subject", "duration_minutes"]
DEFAULT_SUBJECT = "System Design"


def ensure_directories():
    for path in (DATA_DIR, DAILY_LOG_DIR, MONTHLY_SUMMARY_DIR, METADATA_DIR):
        path.mkdir(parents=True, exist_ok=True)
