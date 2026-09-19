import logging
import time

import cv2
import numpy as np

from ..config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, TARGET_FPS, DEMO_MODE

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

    def open(self) -> bool:
        if DEMO_MODE:
            logger.info("Demo mode: skipping camera open")
            self.is_opened = True
            return True
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                logger.warning("Cannot open camera %d", self.camera_index)
                return False
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
            self.is_opened = True
            logger.info("Camera %d opened", self.camera_index)
            return True
        except Exception as e:
            logger.error("Camera open error: %s", e)
            return False

    def read(self) -> tuple[bool, np.ndarray | None]:
        if DEMO_MODE:
            return True, self._generate_demo_frame()
        if not self.is_opened or self.cap is None:
            return False, None
        now = time.time()
        if now - self.last_frame_time < self.frame_interval:
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
        cv2.putText(frame, "DEMO MODE", (self.frame_width // 2 - 100, self.frame_height // 2),
                     cv2.FONT_HERSHEY_SIMPLEX, 1.0, (200, 200, 200), 2)
        self._update_fps()
        return frame

    def _update_fps(self):
        self.fps_counter += 1
        now = time.time()
        if now - self.fps_timer >= 1.0:
            self.current_fps = self.fps_counter / (now - self.fps_timer)
            self.fps_counter = 0
            self.fps_timer = now

    def release(self):
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
