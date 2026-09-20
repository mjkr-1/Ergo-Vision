import logging
import threading
import time

import cv2
import numpy as np

from ..config import CAMERA_INDEX, DEMO_MODE, FRAME_HEIGHT, FRAME_WIDTH, TARGET_FPS

logger = logging.getLogger(__name__)


class Camera:
    def __init__(self, camera_index: int = CAMERA_INDEX):
        self.camera_index = camera_index
        self.cap = None
        self.is_opened = False
        self.frame_width = FRAME_WIDTH
        self.frame_height = FRAME_HEIGHT
        self.target_fps = TARGET_FPS
        self.frame_interval = 1.0 / self.target_fps
        self.last_frame_time = 0.0
        self.fps_counter = 0
        self.fps_timer = time.time()
        self.current_fps = 0.0
        self._lock = threading.RLock()

    def open(self) -> bool:
        with self._lock:
            if DEMO_MODE:
                logger.info("Demo mode: skipping camera open")
                self.is_opened = True
                return True
            return self._open_index(self.camera_index)

    def _open_index(self, index: int) -> bool:
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            cap.release()
            logger.warning("Cannot open camera %d", index)
            return False

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        self.cap = cap
        self.camera_index = index
        self.is_opened = True
        self.last_frame_time = 0.0
        self.current_fps = 0.0
        logger.info("Camera %d opened", index)
        return True

    def select(self, index: int) -> bool:
        if index < 0 or index > 12:
            return False
        with self._lock:
            if DEMO_MODE:
                self.camera_index = index
                return True
            old_index = self.camera_index
            if index == old_index and self.is_opened:
                return True
            if self.cap is not None:
                self.cap.release()
            self.cap = None
            self.is_opened = False
            if self._open_index(index):
                return True
            logger.warning("Camera %d unavailable; restoring camera %d", index, old_index)
            self._open_index(old_index)
            return False

    def scan(self, max_index: int = 5) -> list[int]:
        if DEMO_MODE:
            return [self.camera_index]
        found: list[int] = []
        with self._lock:
            for index in range(max_index):
                if index == self.camera_index and self.is_opened:
                    found.append(index)
                    continue
                cap = cv2.VideoCapture(index)
                try:
                    if cap.isOpened():
                        found.append(index)
                finally:
                    cap.release()
        return found

    def read(self) -> tuple[bool, np.ndarray | None]:
        with self._lock:
            if not self.is_opened:
                return False, None
            now = time.time()
            if now - self.last_frame_time < self.frame_interval:
                return False, None
            if DEMO_MODE:
                frame = self._generate_demo_frame()
                self.last_frame_time = now
                self._update_fps()
                return True, frame
            if self.cap is None:
                return False, None
            ret, frame = self.cap.read()
            if not ret or frame is None:
                return False, None
            self.last_frame_time = now
            self._update_fps()
            return True, frame

    def _generate_demo_frame(self) -> np.ndarray:
        frame = np.zeros((self.frame_height, self.frame_width, 3), dtype=np.uint8)
        frame[:] = (40, 40, 40)
        cv2.putText(frame, "DEMO MODE", (self.frame_width // 2 - 100, self.frame_height // 2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (200, 200, 200), 2)
        return frame

    def _update_fps(self):
        self.fps_counter += 1
        now = time.time()
        if now - self.fps_timer >= 1.0:
            self.current_fps = self.fps_counter / (now - self.fps_timer)
            self.fps_counter = 0
            self.fps_timer = now

    def release(self):
        with self._lock:
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            self.is_opened = False

    def get_status(self) -> dict:
        return {
            "camera_index": self.camera_index,
            "is_opened": self.is_opened,
            "current_fps": round(self.current_fps, 1),
            "frame_width": self.frame_width,
            "frame_height": self.frame_height,
        }
