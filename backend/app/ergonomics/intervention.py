from __future__ import annotations

from dataclasses import asdict, dataclass
import time

from .geometry import clamp


@dataclass
class InterventionSnapshot:
    state: str = "NORMAL"
    active: bool = False
    trigger_seconds: float = 5.0
    recovery_required_seconds: float = 2.0
    pending_seconds: float = 0.0
    verification_seconds: float = 0.0
    correction_seconds: float = 0.0
    risk_before: float = 0.0
    risk_after: float = 0.0
    improvement_percent: float = 0.0
    total_interventions: int = 0
    successful_corrections: int = 0
    correction_rate_percent: float = 0.0

    def as_dict(self) -> dict:
        return asdict(self)


class InterventionEngine:
    """Closed-loop alert state machine.

    The in-app alert becomes active only after sustained poor posture and clears
    only after reliable GOOD posture is held continuously for the recovery
    window. LOW_CONFIDENCE never counts as a successful correction.
    """

    def __init__(
        self,
        trigger_seconds: float = 5.0,
        recovery_seconds: float = 2.0,
        corrected_display_seconds: float = 1.6,
        poor_risk_threshold: float = 0.35,
        recovery_risk_threshold: float = 0.30,
    ):
        self.trigger_seconds = max(1.0, trigger_seconds)
        self.recovery_seconds = max(0.5, recovery_seconds)
        self.corrected_display_seconds = max(0.5, corrected_display_seconds)
        self.poor_risk_threshold = clamp(poor_risk_threshold, 0.0, 1.0)
        self.recovery_risk_threshold = clamp(recovery_risk_threshold, 0.0, 1.0)
        self.reset()

    def reset(self) -> None:
        self._state = "NORMAL"
        self._poor_started: float | None = None
        self._good_started: float | None = None
        self._alert_started: float | None = None
        self._corrected_started: float | None = None
        self._pending_peak_risk = 0.0
        self._risk_before = 0.0
        self._risk_after = 0.0
        self._correction_seconds = 0.0
        self._improvement_percent = 0.0
        self._total = 0
        self._success = 0
        self._snapshot = InterventionSnapshot(
            trigger_seconds=self.trigger_seconds,
            recovery_required_seconds=self.recovery_seconds,
        )

    def pause(self) -> None:
        self._state = "NORMAL"
        self._poor_started = None
        self._good_started = None
        self._alert_started = None
        self._corrected_started = None
        self._pending_peak_risk = 0.0
        self._snapshot = self._emit(time.monotonic())

    def current(self) -> InterventionSnapshot:
        return self._snapshot

    def update(
        self,
        risk: float,
        posture_status: str,
        reliable: bool,
        timestamp: float | None = None,
    ) -> InterventionSnapshot:
        now = time.monotonic() if timestamp is None else float(timestamp)
        risk = clamp(float(risk), 0.0, 1.0)
        poor = reliable and posture_status in ("WARNING", "BAD") and risk >= self.poor_risk_threshold
        good = reliable and posture_status == "GOOD" and risk <= self.recovery_risk_threshold

        if self._state == "CORRECTED":
            if self._corrected_started is not None and now - self._corrected_started >= self.corrected_display_seconds:
                self._state = "NORMAL"
                self._poor_started = None
                self._good_started = None
                self._alert_started = None
                self._corrected_started = None
                self._pending_peak_risk = 0.0
            return self._emit(now)

        if self._state in ("NORMAL", "PENDING"):
            if poor:
                if self._poor_started is None:
                    self._poor_started = now
                    self._pending_peak_risk = risk
                    self._state = "PENDING"
                self._pending_peak_risk = max(self._pending_peak_risk, risk)
                if now - self._poor_started >= self.trigger_seconds:
                    self._state = "ALERTING"
                    self._alert_started = now
                    self._risk_before = max(self._pending_peak_risk, risk)
                    self._total += 1
            else:
                self._state = "NORMAL"
                self._poor_started = None
                self._pending_peak_risk = 0.0
            return self._emit(now)

        if self._state == "ALERTING":
            if good:
                self._state = "VERIFYING"
                self._good_started = now
            else:
                self._good_started = None
            return self._emit(now)

        if self._state == "VERIFYING":
            if not reliable:
                self._state = "ALERTING"
                self._good_started = None
            elif poor:
                self._state = "ALERTING"
                self._good_started = None
            elif good:
                if self._good_started is None:
                    self._good_started = now
                if now - self._good_started >= self.recovery_seconds:
                    self._state = "CORRECTED"
                    self._corrected_started = now
                    self._risk_after = risk
                    if self._alert_started is not None:
                        self._correction_seconds = max(0.0, now - self._alert_started)
                    if self._risk_before > 1e-6:
                        self._improvement_percent = clamp(
                            (self._risk_before - self._risk_after) / self._risk_before * 100.0,
                            0.0,
                            100.0,
                        )
                    else:
                        self._improvement_percent = 0.0
                    self._success += 1
            else:
                self._state = "ALERTING"
                self._good_started = None
            return self._emit(now)

        return self._emit(now)

    def _emit(self, now: float) -> InterventionSnapshot:
        pending = 0.0
        if self._poor_started is not None and self._state == "PENDING":
            pending = max(0.0, now - self._poor_started)
        verification = 0.0
        if self._good_started is not None and self._state == "VERIFYING":
            verification = max(0.0, now - self._good_started)
        rate = self._success / self._total * 100.0 if self._total else 0.0
        self._snapshot = InterventionSnapshot(
            state=self._state,
            active=self._state in ("ALERTING", "VERIFYING"),
            trigger_seconds=self.trigger_seconds,
            recovery_required_seconds=self.recovery_seconds,
            pending_seconds=round(pending, 2),
            verification_seconds=round(verification, 2),
            correction_seconds=round(self._correction_seconds, 2),
            risk_before=round(self._risk_before, 4),
            risk_after=round(self._risk_after, 4),
            improvement_percent=round(self._improvement_percent, 1),
            total_interventions=self._total,
            successful_corrections=self._success,
            correction_rate_percent=round(rate, 1),
        )
        return self._snapshot
