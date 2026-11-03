from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4


@dataclass
class StudySession:
    subject: str
    start_time: datetime
    monotonic_start: float
    session_id: str

    @classmethod
    def start(cls, subject: str, monotonic_start: float):
        return cls(
            subject=subject.strip(),
            start_time=datetime.now(),
            monotonic_start=monotonic_start,
            session_id=str(uuid4()),
        )
