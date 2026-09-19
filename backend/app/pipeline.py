import json
import logging
import threading
import time
from datetime import datetime, timezone
from typing import Optional

import numpy as np

from .config import WEBSOCKET_UPDATE_INTERVAL, SCORE_GOOD_THRESHOLD, SCORE_WARNING_THRESHOLD
from .ergonomics.classifier import PostureClassifier
from .ergonomics.feedback import FeedbackEngine
from .ergonomics.measurements import ErgonomicMeasurements, compute_measurements
from .ergonomics.scoring import compute_score
from .ergonomics.smoothing import SmoothingBuffer
from .session.tracker import SessionTracker
from .vision.camera import Camera
from .vision.detector import Detector

logger = logging.getLogger(__name__)


class PosturePipeline:
    """Runs the full CV pipeline in a background thread."""

    def __init__(self, camera: Camera, detector: Detector):
        self.camera = camera
        self.detector = detector
        self.classifier = PostureClassifier()
        self.feedback_engine = FeedbackEngine()
        self.smoother = SmoothingBuffer()
        self.tracker = SessionTracker()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._last_update_time = 0.0
        self._current_measurements = ErgonomicMeasurements(person_detected=False)
        self._current_status = "NO_PERSON"
        self._current_score = 0
        self._last_event = None

    def start(self):
        if self._running:
            return
        self._running = True
        self.tracker.start()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Pipeline started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
        self.tracker.stop()
        logger.info("Pipeline stopped")

    def _run_loop(self):
        while self._running:
            ok, frame = self.camera.read()
            if not ok or frame is None:
                time.sleep(0.01)
                continue

            landmarks, _annotated = self.detector.process_frame(frame)
            measurements = compute_measurements(landmarks)
            smoothed = self.smoother.smooth(measurements)
            status = self.classifier.classify(smoothed)
            score, _breakdown = compute_score(smoothed)

            with self._lock:
                self._current_measurements = smoothed
                self._current_status = status
                self._current_score = score
                self.tracker.update(status, score)

            self._maybe_emit(status, smoothed, score)

            time.sleep(0.01)

    def _maybe_emit(self, status, measurements, score):
        now = time.time()
        if now - self._last_update_time < WEBSOCKET_UPDATE_INTERVAL:
            return
        self._last_update_time = now
        self._last_event = self._build_event(status, measurements, score)

    def _build_event(self, status, measurements, score) -> dict:
        feedback = self.feedback_engine.generate(measurements, status)
        return {
            "score": score,
            "status": status,
            "measurements": {
                "head_tilt_degrees": round(measurements.head_tilt_degrees, 1),
                "shoulder_alignment_score": round(measurements.shoulder_alignment_score, 2),
                "shoulder_alignment_degrees": round(measurements.shoulder_alignment_degrees, 1),
                "neck_offset": round(measurements.neck_offset, 3),
                "forward_head_indicator": round(measurements.forward_head_indicator, 2),
                "gaze_vertical_degrees": round(measurements.gaze_vertical_degrees, 1),
            },
            "feedback": feedback,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "person_detected": measurements.person_detected,
        }

    def get_current(self) -> dict:
        with self._lock:
            measurements = self._current_measurements
            status = self._current_status
            score = self._current_score
        return self._build_event(status, measurements, score)

    def get_last_event(self) -> Optional[dict]:
        return self._last_event

    def get_session_stats(self) -> dict:
        stats = self.tracker.get_stats()
        return stats.__dict__
