# Study Tracker

Python 3.10+. Install Matplotlib for charts: `python3 -m pip install matplotlib`

Run from this directory with `python3 main.py`.

Keys: S start, E end, R summary, P plots, C change subject,
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

### Plotting archived and active months

Plotting reads the retained monthly summaries. If a past or current month is
active and its summary is missing or invalid, the tracker rebuilds it from that
month's daily CSV logs before plotting. Archived months are read-only and are
plotted from their retained summaries; the tracker never tries to rebuild an
archived month. If an active month's summary cannot be recovered because its
daily logs are missing or corrupt, plotting reports the problem instead of
silently treating that month as zero study time. Future months are zero-filled.



### Summary menu

Choose **R – Summary**, then select a period:
- **D – Day:** enter a date (`YYYY-MM-DD`).
- **M – Month:** enter a month (`YYYY-MM`, blank for the current month).
- **Q – Quarter:** enter a quarter (1–4) and year.
- **Y – Year:** enter a year (blank for the current year).

The summary totals study time by subject and shows the combined total. For active
months, missing or invalid monthly summaries are rebuilt from daily logs before
the summary is displayed. Archived months are read-only and are displayed from
their retained summaries; they are never rebuilt. If an active month's data
cannot be recovered from its daily logs, the summary reports the error.
