import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class SessionStats:
    session_duration_seconds: float = 0.0
    good_duration_seconds: float = 0.0
    warning_duration_seconds: float = 0.0
    bad_duration_seconds: float = 0.0
    no_person_duration_seconds: float = 0.0
    good_percentage: float = 0.0
    warning_percentage: float = 0.0
    bad_percentage: float = 0.0
    no_person_percentage: float = 0.0
    warning_count: int = 0
    bad_count: int = 0
    average_score: float = 100.0
    current_score: int = 100
    longest_poor_posture_seconds: float = 0.0
    active: bool = False


class SessionTracker:
    def __init__(self):
        self._lock = threading.RLock()
        self._start_time: float | None = None
        self._good_seconds = 0.0
        self._warning_seconds = 0.0
        self._bad_seconds = 0.0
        self._no_person_seconds = 0.0
        self._warning_count = 0
        self._bad_count = 0
        self._scores: list[int] = []
        self._current_score = 100
        self._last_status = "UNKNOWN"
        self._last_frame_time: float | None = None
        self._current_poor_started: float | None = None
        self._longest_poor = 0.0
        self._session_id: str | None = None
        self._posture_alert_count = 0
        self._movement_alert_count = 0
        self.active = False

    def start(self):
        with self._lock:
            if self.active:
                return
            now = time.time()
            if self._start_time is None:
                self._start_time = now
                self._session_id = str(uuid.uuid4())
            self.active = True
            self._last_frame_time = now
            if self._last_status in ("WARNING", "BAD"):
                self._current_poor_started = now

    def stop(self):
        with self._lock:
            if not self.active:
                return
            now = time.time()
            self._accumulate_interval(now)
            self._finalize_poor_period(now)
            self.active = False
            self._last_frame_time = None

    def reset(self):
        with self._lock:
            self._start_time = None
            self._good_seconds = 0.0
            self._warning_seconds = 0.0
            self._bad_seconds = 0.0
            self._no_person_seconds = 0.0
            self._warning_count = 0
            self._bad_count = 0
            self._scores = []
            self._current_score = 100
            self._last_status = "UNKNOWN"
            self._last_frame_time = None
            self._current_poor_started = None
            self._longest_poor = 0.0
            self._session_id = None
            self._posture_alert_count = 0
            self._movement_alert_count = 0
            self.active = False

    def record_alert(self, kind: str) -> None:
        with self._lock:
            if kind == "posture":
                self._posture_alert_count += 1
            elif kind == "movement":
                self._movement_alert_count += 1

    def report_record(self) -> dict | None:
        with self._lock:
            if self._session_id is None or self._start_time is None:
                return None
            stats = self.get_stats()
            ended = time.time()
            return {
                "session_id": self._session_id,
                "started_at": datetime.fromtimestamp(self._start_time, timezone.utc).isoformat(),
                "ended_at": datetime.fromtimestamp(ended, timezone.utc).isoformat(),
                "monitored_seconds": stats.session_duration_seconds,
                "good_seconds": stats.good_duration_seconds,
                "warning_seconds": stats.warning_duration_seconds,
                "bad_seconds": stats.bad_duration_seconds,
                "away_seconds": stats.no_person_duration_seconds,
                "average_score": stats.average_score,
                "warning_count": stats.warning_count,
                "bad_count": stats.bad_count,
                "posture_alert_count": self._posture_alert_count,
                "movement_alert_count": self._movement_alert_count,
            }

    def update(self, status: str, score: int):
        with self._lock:
            if self._start_time is None:
                self.start()
            elif not self.active:
                return

            now = time.time()
            self._accumulate_interval(now)

            if status != self._last_status:
                if status == "WARNING":
                    self._warning_count += 1
                if status == "BAD":
                    self._bad_count += 1
                if status in ("WARNING", "BAD") and self._current_poor_started is None:
                    self._current_poor_started = now
                if status in ("GOOD", "NO_PERSON"):
                    self._finalize_poor_period(now)

            self._last_status = status
            if self._current_poor_started is not None:
                self._longest_poor = max(
                    self._longest_poor,
                    now - self._current_poor_started,
                )

            self._current_score = score
            self._scores.append(score)
            if len(self._scores) > 10000:
                self._scores = self._scores[-10000:]
            self._last_frame_time = now

    def get_stats(self) -> SessionStats:
        with self._lock:
            good = self._good_seconds
            warning = self._warning_seconds
            bad = self._bad_seconds
            no_person = self._no_person_seconds

            if self.active and self._last_frame_time is not None:
                dt = max(0.0, time.time() - self._last_frame_time)
                if self._last_status == "GOOD":
                    good += dt
                elif self._last_status == "WARNING":
                    warning += dt
                elif self._last_status == "BAD":
                    bad += dt
                elif self._last_status == "NO_PERSON":
                    no_person += dt

            status_seconds = good + warning + bad + no_person

            def pct(secs):
                if status_seconds <= 0:
                    return 0.0
                return round(secs / status_seconds * 100.0, 1)

            avg = round(sum(self._scores) / len(self._scores), 1) if self._scores else 100.0
            longest_poor = self._longest_poor
            if self.active and self._current_poor_started is not None:
                longest_poor = max(longest_poor, time.time() - self._current_poor_started)

            return SessionStats(
                session_duration_seconds=round(status_seconds, 1),
                good_duration_seconds=round(good, 1),
                warning_duration_seconds=round(warning, 1),
                bad_duration_seconds=round(bad, 1),
                no_person_duration_seconds=round(no_person, 1),
                good_percentage=pct(good),
                warning_percentage=pct(warning),
                bad_percentage=pct(bad),
                no_person_percentage=pct(no_person),
                warning_count=self._warning_count,
                bad_count=self._bad_count,
                average_score=avg,
                current_score=self._current_score,
                longest_poor_posture_seconds=round(longest_poor, 1),
                active=self.active,
            )

    def get_current_status(self) -> str:
        with self._lock:
            return self._last_status

    def _accumulate_interval(self, now: float):
        if self._last_frame_time is None:
            return
        dt = max(0.0, now - self._last_frame_time)
        if self._last_status == "GOOD":
            self._good_seconds += dt
        elif self._last_status == "WARNING":
            self._warning_seconds += dt
        elif self._last_status == "BAD":
            self._bad_seconds += dt
        elif self._last_status == "NO_PERSON":
            self._no_person_seconds += dt

    def _finalize_poor_period(self, now: float):
        if self._current_poor_started is None:
            return
        self._longest_poor = max(
            self._longest_poor,
            now - self._current_poor_started,
        )
        self._current_poor_started = None
