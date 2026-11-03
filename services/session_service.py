import time
from datetime import datetime

from models.session import StudySession
from storage.daily_logs import append_session
from services.summary_service import update_summary_for_session


class SessionService:
    def __init__(self):
        self.active_session = None

    def start(self, subject: str):
        if self.active_session is not None:
            raise RuntimeError("A session is already active")
        if not subject.strip():
            raise ValueError("Subject cannot be empty")
        self.active_session = StudySession.start(subject, time.monotonic())

    def elapsed_minutes(self):
        if self.active_session is None:
            return 0
        seconds = time.monotonic() - self.active_session.monotonic_start
        return max(0, int(seconds / 60 + 0.5))

    def finish(self):
        session = self.active_session
        if session is None:
            return None

        seconds = max(0.0, time.monotonic() - session.monotonic_start)
        minutes = max(0, int(seconds / 60 + 0.5))
        end_time = datetime.now().replace(second=0, microsecond=0)
        start_day = session.start_time.date()
        row = {
            "session_id": session.session_id,
            "subject": session.subject,
            "start_time": session.start_time.isoformat(timespec="minutes"),
            "end_time": end_time.isoformat(timespec="minutes"),
            "duration_minutes": minutes,
        }

        # Once the daily append succeeds, clear the active session. If the
        # summary update fails, rebuild from daily logs rather than appending twice.
        append_session(start_day, row)
        self.active_session = None
        update_summary_for_session(session.subject, start_day, minutes)
        return session.subject, minutes
