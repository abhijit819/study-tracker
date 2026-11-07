# Study Tracker

Python 3.10+. Install Matplotlib for charts: `python3 -m pip install matplotlib`

Run from this directory with `python3 main.py`.

Keys: S start, E end, T elapsed time, R summary, P plots, C change subject,
V view subjects, B rebuild month, A archive completed month, Q quit.

Data is stored under `data/`:
- `daily_logs/YYYY-MM-DD.csv`: individual sessions
- `monthly_summaries/YYYY-MM.csv`: daily totals by subject
- `metadata/archives.json`: archive state and summary checksums
- `metadata/subjects.json`: known subjects and the last selected subject

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

Choose **R – Summary**, then select:
- **D – Day:** enter year, month, and day in sequence. Each blank input
  defaults to the current year, month, or day respectively. If the current
  day does not exist in the selected month, the default is the month's last day.
- **M – Month:** enter a month (`YYYY-MM`, blank for the current month).
- **Y – Year:** enter a year (blank for the current year).

Summaries total study time by subject and show a combined total. A month with
no summary and no daily log files is treated as zero study time. Consequently,
missing months in a yearly summary contribute zero rather than causing an error.
If a summary is missing but daily logs exist, the summary is rebuilt from those
logs. Corrupt daily logs or an unrecoverable corrupt summary still produce an
error. Archived months remain read-only and must have a valid retained summary.


### Subject management and plotting

The selected subject is restored when the application starts and saved when
you quit normally. Use **C – Change subject** to introduce or switch subjects,
and **V – View subjects** to list all known subjects. Existing daily logs and
monthly summaries are scanned when metadata is loaded, so subjects recorded
before this feature existed are discovered automatically.

Subject identity is case-insensitive (`System Design`, `system design`, and
`SYSTEM DESIGN` refer to the same subject). Existing CSV files are not rewritten
just to change capitalization; historical spellings are merged when summaries
and plots are aggregated. New entries reuse the existing subject's spelling.

When plotting all subjects, the chart displays one line for total study time
across subjects rather than one line per subject. The single-subject plot option
continues to show an individual subject.
