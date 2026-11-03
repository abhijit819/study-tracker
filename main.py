from config import DEFAULT_SUBJECT, ensure_directories
from services.session_service import SessionService
from services.summary_service import ensure_current_month_summary_exists
from services.archive_service import resume_interrupted_archives
from ui.keyboard import get_key
from ui.menu import (
    archive_month_menu, format_minutes, plot_menu, rebuild_month, show_summary,
)


def format_elapsed(seconds):
    total_seconds = int(seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def main():
    ensure_directories()
    for message in resume_interrupted_archives():
        print(message)
    ensure_current_month_summary_exists()

    service = SessionService()
    current_subject = DEFAULT_SUBJECT
    print("Study Tracker")

    while True:
        if service.active_session:
            print(
                f"\nActive: {service.active_session.subject} "
                f"({format_elapsed(service.elapsed_seconds())} elapsed)"
            )
        else:
            print(f"\nCurrent subject: {current_subject}")

        print("[S] Start  [E] End  [T] Elapsed time  [R] Summary  [P] Plot")
        print("[C] Change subject  [B] Rebuild month  [A] Archive month  [Q] Quit")
        choice = get_key()

        if choice == "S":
            if service.active_session:
                print("A session is already active.")
            else:
                service.start(current_subject)
                started_at = service.active_session.start_time.strftime("%I:%M:%S %p")
                print(f"Started: {current_subject} at {started_at}")
        elif choice == "T":
            elapsed = service.elapsed_seconds()
            if elapsed is None:
                print("No session in progress")
            else:
                print(f"Elapsed time: {format_elapsed(elapsed)}")
        elif choice == "E":
            try:
                result = service.finish()
                if result is None:
                    print("No active session.")
                else:
                    print(f"Saved {result[0]}: {format_minutes(result[1])}")
            except Exception as exc:
                print(f"Daily log was saved but summary update failed: {exc}")
                print("Use [B] to rebuild that unarchived month's summary.")
        elif choice == "R":
            show_summary()
        elif choice == "P":
            plot_menu()
        elif choice == "C":
            if service.active_session:
                print("Ending the active session before changing subject...")
                try:
                    result = service.finish()
                    if result:
                        print(f"Saved {result[0]}: {format_minutes(result[1])}")
                except Exception as exc:
                    print(f"Could not save active session; subject unchanged: {exc}")
                    continue
            new_subject = input("New subject: ").strip()
            if new_subject:
                current_subject = new_subject
        elif choice == "B":
            rebuild_month()
        elif choice == "A":
            if service.active_session:
                print("End the active session before archiving.")
            else:
                archive_month_menu()
        elif choice == "Q":
            if service.active_session:
                try:
                    result = service.finish()
                    if result:
                        print(f"Saved {result[0]}: {format_minutes(result[1])}")
                except Exception as exc:
                    print(f"Could not save active session: {exc}")
                    print("Quit cancelled so you can resolve the save problem.")
                    continue
            print("Goodbye.")
            break
        else:
            print("Unknown option.")


if __name__ == "__main__":
    main()
