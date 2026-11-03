# Study Tracker

Python 3.10+. Install Matplotlib for charts: `python3 -m pip install matplotlib`

Run from this directory with `python3 main.py`.

Keys: S start, E end, R monthly summary, P plots, C change subject,
B rebuild month, A archive completed month, Q quit.

Data is stored under `data/`:
- `daily_logs/YYYY-MM-DD.csv`: individual sessions
- `monthly_summaries/YYYY-MM.csv`: daily totals by subject
- `metadata/archives.json`: archive state and summary checksums

A session is appended to its daily log, then the monthly summary is updated.
If the process stops between those writes, rebuild that unarchived month's
summary from daily logs.

Archiving first tries to rebuild the summary from daily logs. If those logs
are unusable, it falls back to a structurally valid summary maintained during
session saves. If neither is valid, archiving aborts without deleting logs.
After archiving, the monthly summary is retained read-only and daily logs are
deleted. Archived months cannot be rebuilt or updated through the application.

Read-only permissions guard against accidental writes, not deliberate changes
by a user with sufficient permissions. A SHA-256 checksum in the archive
manifest detects changes to archived summaries.

The aggregation layer supports day, month, quarter, and year granularity.
