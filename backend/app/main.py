import logging
import time
from contextlib import asynccontextmanager

import cv2
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from .api import routes
from .config import DEMO_MODE, FRAME_WIDTH, FRAME_HEIGHT
from .logger import setup_logging
from .pipeline import PosturePipeline
from .vision.camera import Camera
from .vision.detector import Detector

setup_logging()
logger = logging.getLogger(__name__)

_active_pipeline = None
_start_time = time.time()


def get_pipeline():
    return _active_pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _active_pipeline
    camera = Camera()
    detector = Detector(camera)
    pipeline = PosturePipeline(camera, detector)
    _active_pipeline = pipeline

    if not DEMO_MODE:
        models_loaded = detector.load_models()
        if not models_loaded:
            logger.warning("Failed to load MediaPipe models.")
        camera_opened = camera.open()
        if not camera_opened:
            logger.warning("Camera unavailable. Running without live video input.")
        if not camera_opened or not models_loaded:
            logger.warning("Vision pipeline partially initialized.")
    else:
        logger.info("Demo mode active. Camera and models not used.")

    pipeline.start()
    logger.info("ErgoVision started")
    yield
    if _active_pipeline:
        _active_pipeline.stop()
        _active_pipeline.detector.release()
        _active_pipeline = None


app = FastAPI(title="ErgoVision", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)


@app.websocket("/ws/posture")
async def ws_posture(websocket: WebSocket):
    from .api.websocket import websocket_endpoint
    await websocket_endpoint(websocket)


def stream_generator():
    global _active_pipeline
    pipeline = _active_pipeline
    if pipeline is None:
        while True:
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + _blank_frame("Backend not ready") + b"\r\n"
            time.sleep(0.1)

    while True:
        annotated = None
        camera = pipeline.camera
        if DEMO_MODE:
            ok, frame = camera.read()
            if ok and frame is not None:
                _, annotated = pipeline.detector.process_frame(frame)
        elif camera.is_opened:
            ok, frame = camera.read()
            if ok and frame is not None:
                _, annotated = pipeline.detector.process_frame(frame)

        if annotated is None:
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + _blank_frame("No camera signal") + b"\r\n"
            time.sleep(0.1)
            continue

        ret, jpeg = cv2.imencode(".jpg", annotated)
        if not ret:
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + b"\r\n"
            time.sleep(0.1)
            continue
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n"
        time.sleep(0.03)


def _blank_frame(text: str) -> bytes:
    import numpy as np
    frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
    cv2.putText(frame, text, (50, FRAME_HEIGHT // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (180, 180, 180), 2)
    ret, jpeg = cv2.imencode(".jpg", frame)
    return jpeg.tobytes()


@app.get("/api/stream")
def video_stream():
    from fastapi.responses import StreamingResponse
    return StreamingResponse(stream_generator(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/api/stream/frame")
def video_frame():
    from fastapi.responses import Response
    pipeline = _active_pipeline
    if pipeline is None:
        return Response(status_code=503)
    ok, frame = pipeline.camera.read()
    if not ok or frame is None:
        return Response(content=_blank_frame("No camera signal"), media_type="image/jpeg")
    _, annotated = pipeline.detector.process_frame(frame)
    ret, jpeg = cv2.imencode(".jpg", annotated)
    if not ret:
        return Response(status_code=500)
    return Response(content=jpeg.tobytes(), media_type="image/jpeg", headers={"Cache-Control": "no-store"})