import time
from dataclasses import dataclass, field


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
        self._start_time: float | None = None
        self._good_seconds = 0.0
        self._warning_seconds = 0.0
        self._bad_seconds = 0.0
        self._no_person_seconds = 0.0
        self._warning_count = 0
        self._bad_count = 0
        self._scores: list[int] = []
        self._current_score = 100
        self._current_status = "UNKNOWN"
        self._last_status = "UNKNOWN"
        self._last_frame_time: float | None = None
        self._current_poor_started: float | None = None
        self._longest_poor = 0.0
        self.active = False

    def start(self):
        if self.active:
            return
        self._start_time = time.time()
        self.active = True

    def stop(self):
        self.active = False

    def reset(self):
        self._start_time = None
        self._good_seconds = 0.0
        self._warning_seconds = 0.0
        self._bad_seconds = 0.0
        self._no_person_seconds = 0.0
        self._warning_count = 0
        self._bad_count = 0
        self._scores = []
        self._current_score = 100
        self._current_status = "UNKNOWN"
        self._last_status = "UNKNOWN"
        self._last_frame_time = None
        self._current_poor_started = None
        self._longest_poor = 0.0
        self.active = False

    def update(self, status: str, score: int):
        now = time.time()
        if not self._start_time:
            self.start()

        if self._last_frame_time is not None and self.active:
            dt = now - self._last_frame_time
            state = self._last_status if self._last_status else status
            if state == "GOOD":
                self._good_seconds += dt
            elif state == "WARNING":
                self._warning_seconds += dt
            elif state == "BAD":
                self._bad_seconds += dt
            elif state == "NO_PERSON":
                self._no_person_seconds += dt

        if status != self._last_status:
            if status == "WARNING":
                self._warning_count += 1
            if status == "BAD":
                self._bad_count += 1
            if status in ("WARNING", "BAD") and self._current_poor_started is None:
                self._current_poor_started = now
            if status in ("GOOD", "NO_PERSON") and self._current_poor_started is not None:
                poor_duration = now - self._current_poor_started
                if poor_duration > self._longest_poor:
                    self._longest_poor = poor_duration
                self._current_poor_started = None

        self._last_status = status
        if self._current_poor_started is not None:
            poor_duration = now - self._current_poor_started
            if poor_duration > self._longest_poor:
                self._longest_poor = poor_duration

        self._current_score = score
        self._scores.append(score)
        if len(self._scores) > 10000:
            self._scores = self._scores[-10000:]
        self._last_frame_time = now

    def get_stats(self) -> SessionStats:
        now = time.time()
        status_seconds = self._good_seconds + self._warning_seconds + self._bad_seconds + self._no_person_seconds

        duration = (now - self._start_time) if self._start_time else 0.0
        duration = max(duration, status_seconds)

        def pct(secs):
            if status_seconds <= 0:
                return 0.0
            return round(secs / status_seconds * 100.0, 1)

        avg = round(sum(self._scores) / len(self._scores), 1) if self._scores else 100.0

        return SessionStats(
            session_duration_seconds=round(duration, 1),
            good_duration_seconds=round(self._good_seconds, 1),
            warning_duration_seconds=round(self._warning_seconds, 1),
            bad_duration_seconds=round(self._bad_seconds, 1),
            no_person_duration_seconds=round(self._no_person_seconds, 1),
            good_percentage=pct(self._good_seconds),
            warning_percentage=pct(self._warning_seconds),
            bad_percentage=pct(self._bad_seconds),
            no_person_percentage=pct(self._no_person_seconds),
            warning_count=self._warning_count,
            bad_count=self._bad_count,
            average_score=avg,
            current_score=self._current_score,
            longest_poor_posture_seconds=round(self._longest_poor, 1),
            active=self.active,
        )

    def get_current_status(self) -> str:
        return self._last_status