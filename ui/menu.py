from datetime import date, datetime
import calendar

from ui.keyboard import get_key
from services.summary_service import get_month_totals, month_key, rebuild_month_summary
from services.archive_service import archive_month
from storage.archive_registry import get_month_state
from reporting.aggregation import get_study_data
from reporting.plotting import plot_study_data


def format_minutes(minutes):
    hours, mins = divmod(minutes, 60)
    parts = []
    if hours:
        parts.append(f"{hours} hour" + ("" if hours == 1 else "s"))
    if mins or not hours:
        parts.append(f"{mins} minute" + ("" if mins == 1 else "s"))
    return " ".join(parts)


def prompt_month():
    raw = input("Month (YYYY-MM, blank for current month): ").strip()
    if not raw:
        today = date.today()
        return today.year, today.month
    parsed = datetime.strptime(raw, "%Y-%m")
    return parsed.year, parsed.month


def prompt_date(label):
    return date.fromisoformat(input(f"{label} (YYYY-MM-DD): ").strip())


def show_month_summary():
    try:
        year, month = prompt_month()
        totals = get_month_totals(year, month)
        print(f"\\nSummary for {calendar.month_name[month]} {year}")
        if not totals:
            print("No study sessions recorded.")
        else:
            for subject, minutes in sorted(totals.items()):
                print(f"  {subject}: {format_minutes(minutes)}")
        print(f"Status: {get_month_state(month_key(year, month))}")
    except Exception as exc:
        print(f"Could not display summary: {exc}")


def rebuild_month():
    try:
        year, month = prompt_month()
        count = rebuild_month_summary(year, month)
        print(f"Rebuilt {year:04d}-{month:02d} from {count} daily log file(s).")
    except Exception as exc:
        print(f"Could not rebuild summary: {exc}")


def archive_month_menu():
    try:
        year, month = prompt_month()
        if (year, month) >= (date.today().year, date.today().month):
            print("Only completed months can be archived.")
            return
        print(f"\\nArchive {year:04d}-{month:02d}?")
        print("The monthly summary will be retained; daily logs will be deleted.")
        if input("Type ARCHIVE to continue: ").strip() != "ARCHIVE":
            print("Cancelled.")
            return
        totals, message = archive_month(year, month)
        for subject, minutes in sorted(totals.items()):
            print(f"  {subject}: {format_minutes(minutes)}")
        print(message)
    except Exception as exc:
        print(f"Archive failed: {exc}")


def plot_menu():
    try:
        print("\\nGranularity: D=daily, M=monthly, Q=quarterly, Y=yearly")
        granularity = {"D": "day", "M": "month", "Q": "quarter", "Y": "year"}.get(
            get_key("Choose granularity: ")
        )
        if not granularity:
            print("Invalid choice.")
            return
        start = prompt_date("Start date")
        end = prompt_date("End date")

        print("\\nPlot: 1=one subject, 2=all subjects, 3=total study time")
        mode = {"1": "one", "2": "all", "3": "total"}.get(get_key("Choose plot: "))
        if not mode:
            print("Invalid choice.")
            return
        subject = input("Subject name: ").strip() if mode == "one" else None
        if mode == "one" and not subject:
            print("Subject cannot be empty.")
            return

        labels, subjects, series = get_study_data(start, end, granularity, subject)
        if mode == "one":
            subjects = [subject] if subject in series else []
        plot_study_data(labels, subjects, series, mode)
    except ImportError:
        print("Matplotlib is required. Install it with: python3 -m pip install matplotlib")
    except Exception as exc:
        print(f"Could not plot data: {exc}")
