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


def prompt_plot_month():
    raw = input("Month number (1-12, blank for current month): ").strip()
    if not raw:
        today = date.today()
        return today.year, today.month
    try:
        month = int(raw)
    except ValueError as exc:
        raise ValueError("Enter a month number from 1 to 12.") from exc
    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12.")
    return date.today().year, month


def prompt_plot_quarter():
    raw_quarter = input("Quarter (1-4): ").strip()
    raw_year = input("Year (YYYY): ").strip()
    try:
        quarter = int(raw_quarter)
        year = int(raw_year)
        if quarter not in range(1, 5):
            raise ValueError
        if year < 1 or year > 9999:
            raise ValueError
    except ValueError as exc:
        raise ValueError("Enter a quarter from 1 to 4 and a valid year.") from exc
    return quarter, year


def prompt_plot_year():
    raw = input(f"Year (blank for {date.today().year}): ").strip()
    if not raw:
        return date.today().year
    try:
        year = int(raw)
        if not 1 <= year <= 9999:
            raise ValueError
        return year
    except ValueError as exc:
        raise ValueError("Enter a valid year number.") from exc


def prompt_date_range():
    start_raw = input("Start date (YYYY-MM-DD): ").strip()
    end_raw = input("End date (YYYY-MM-DD): ").strip()
    try:
        start = date.fromisoformat(start_raw)
        end = date.fromisoformat(end_raw)
    except ValueError as exc:
        raise ValueError("Enter dates in YYYY-MM-DD format.") from exc
    if end < start:
        raise ValueError("End date must not be earlier than start date.")
    return start, end


def show_month_summary():
    try:
        year, month = prompt_month()
        totals = get_month_totals(year, month)
        print(f"\nSummary for {calendar.month_name[month]} {year}")
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
        print(f"\nArchive {year:04d}-{month:02d}?")
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
        print("\nPlot period: D=date range, M=month, Q=quarter, Y=year")
        granularity_choice = get_key("Choose period: ")
        if granularity_choice not in {"D", "M", "Q", "Y"}:
            print("Invalid choice.")
            return

        # D plots individual days across an explicit range.
        # M plots the selected month day-by-day.
        # Q and Y show monthly totals for the selected quarter/year.
        if granularity_choice == "D":
            start, end = prompt_date_range()
            granularity = "day"
        elif granularity_choice == "M":
            year, month = prompt_plot_month()
            start = date(year, month, 1)
            end = date(year, month, calendar.monthrange(year, month)[1])
            granularity = "day"
        elif granularity_choice == "Q":
            quarter, year = prompt_plot_quarter()
            first_month = (quarter - 1) * 3 + 1
            last_month = first_month + 2
            start = date(year, first_month, 1)
            end = date(year, last_month, calendar.monthrange(year, last_month)[1])
            granularity = "month"
        else:
            year = prompt_plot_year()
            start, end = date(year, 1, 1), date(year, 12, 31)
            granularity = "month"

        print("\nPlot: 1=one subject, 2=all subjects, 3=total study time")
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
