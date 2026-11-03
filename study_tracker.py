
import csv
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# --------------------------------------------------
# Configuration
# --------------------------------------------------

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

DEFAULT_SUBJECT = "System Design"

CSV_FIELDS = [
    "subject",
    "start_time",
    "end_time",
    "duration_minutes"
]


# --------------------------------------------------
# Keyboard input (blocking, zero polling)
# --------------------------------------------------

def get_key():
    if os.name == "nt":
        import msvcrt
        return msvcrt.getwch().lower()

    import termios
    import tty

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        return sys.stdin.read(1).lower()
    finally:
        termios.tcsetattr(
            fd, termios.TCSADRAIN, old_settings
        )


# --------------------------------------------------
# Logging
# --------------------------------------------------

def get_log_file(date):
    return LOG_DIR / f"{date:%Y-%m-%d}.csv"


def save_session(subject, start_time, end_time, duration_seconds):
    log_file = get_log_file(start_time)

    file_exists = (
        log_file.exists() and log_file.stat().st_size > 0
    )

    duration_minutes = round(duration_seconds / 60)

    with log_file.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "subject": subject,
            "start_time": start_time.isoformat(timespec="minutes"),
            "end_time": end_time.isoformat(timespec="minutes"),
            "duration_minutes": duration_minutes
        })

    print(
        f"\nSession saved: {subject} - "
        f"{format_duration(duration_minutes)}"
    )


# --------------------------------------------------
# Duration formatting
# --------------------------------------------------

def format_duration(minutes):
    minutes = int(minutes)

    hours, remaining_minutes = divmod(minutes, 60)

    parts = []

    if hours:
        parts.append(
            f"{hours} hour{'s' if hours != 1 else ''}"
        )

    if remaining_minutes:
        parts.append(
            f"{remaining_minutes} minute"
            f"{'s' if remaining_minutes != 1 else ''}"
        )

    return " ".join(parts) if parts else "0 minutes"


# --------------------------------------------------
# Summary
# --------------------------------------------------

def show_summary(active_session=None):
    today = datetime.now().date()
    log_file = get_log_file(today)

    totals = {}

    if log_file.exists():
        with log_file.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                subject = row["subject"]
                duration = int(row["duration_minutes"])

                totals[subject] = (
                    totals.get(subject, 0) + duration
                )

    # Include the ongoing session in the summary.
    if active_session is not None:
        subject, start_time, start_mono = active_session

        if start_time.date() == today:
            elapsed_minutes = round(
                (time.monotonic() - start_mono) / 60
            )

            totals[subject] = (
                totals.get(subject, 0) + elapsed_minutes
            )

    print("\n" + "=" * 45)
    print(f" STUDY SUMMARY - {today}")
    print("=" * 45)

    if not totals:
        print("No study sessions recorded today.")
    else:
        grand_total = 0

        for subject, duration in sorted(totals.items()):
            print(
                f"{subject:<25} "
                f"{format_duration(duration)}"
            )
            grand_total += duration

        print("-" * 45)
        print(
            f"{'TOTAL':<25} "
            f"{format_duration(grand_total)}"
        )

    print("=" * 45)


# --------------------------------------------------
# Session management
# --------------------------------------------------

def start_session(subject):
    start_time = datetime.now()
    start_mono = time.monotonic()

    print(
        f"\nStarted studying {subject} at "
        f"{start_time.strftime('%H:%M:%S')}"
    )

    return subject, start_time, start_mono


def end_session(active_session):
    if active_session is None:
        return None

    subject, start_time, start_mono = active_session

    end_time = datetime.now()
    duration = time.monotonic() - start_mono

    save_session(
        subject,
        start_time,
        end_time,
        duration
    )

    return None


# --------------------------------------------------
# Main application
# --------------------------------------------------

def main():

    subject = DEFAULT_SUBJECT
    active_session = None

    print("\n===== STUDY TRACKER =====")

    while True:

        print("\n" + "-" * 35)
        print(f"Current subject : {subject}")

        if active_session is None:
            print("Status          : Not studying")
            print("[S] Start session")
        else:
            print("Status          : Studying")
            print("[E] End session")

        print("[R] Today's summary")
        print("[C] Change subject")
        print("[Q] Quit")

        print("\nPress a key: ", end="", flush=True)

        key = get_key()

        if key == "\x03":
            key = "q"

        print(key.upper())

        # Start session
        if key == "s" and active_session is None:

            active_session = start_session(subject)

        # End session
        elif key == "e" and active_session is not None:

            active_session = end_session(active_session)

        # Display summary
        elif key == "r":

            show_summary(active_session)

        # Change subject
        elif key == "c":

            new_subject = input("\nEnter new subject: ").strip()

            if not new_subject:
                print("Subject unchanged.")
                continue

            # Automatically save the current session.
            if active_session is not None:
                print("\nSaving current session...")
                active_session = end_session(active_session)

            subject = new_subject

            print(f"\nCurrent subject changed to: {subject}")

        # Quit
        elif key == "q":

            if active_session is not None:
                print("\nSaving active session...")
                active_session = end_session(active_session)

            print("\nGoodbye!")
            break

        else:
            print("\nInvalid key or action.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting.")
