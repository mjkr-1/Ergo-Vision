import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

import cv2
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .api import routes
from .config import CORS_ORIGINS, DEMO_MODE, FRAME_HEIGHT, FRAME_WIDTH, STREAM_FPS
from .logger import setup_logging
from .pipeline import PosturePipeline
from .vision.camera import Camera
from .vision.detector import Detector

setup_logging()
logger = logging.getLogger(__name__)

_active_pipeline = None
_start_time = time.time()
_FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


def get_pipeline():
    return _active_pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _active_pipeline
    camera = Camera()
    detector = Detector(camera)
    pipeline = PosturePipeline(camera, detector)
    _active_pipeline = pipeline

    camera_opened = camera.open()
    models_loaded = True if DEMO_MODE else detector.load_models()

    if not camera_opened:
        logger.warning("Camera unavailable. Running without live video input.")
    if not models_loaded:
        logger.warning("MediaPipe models are unavailable.")
    if not camera_opened or not models_loaded:
        logger.warning("Vision pipeline partially initialized.")

    pipeline.start()
    logger.info("ErgoVision started")
    yield

    if _active_pipeline:
        _active_pipeline.stop()
        _active_pipeline.detector.release()
        _active_pipeline = None


app = FastAPI(title="ErgoVision", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(routes.router)


@app.websocket("/ws/posture")
async def ws_posture(websocket: WebSocket):
    from .api.websocket import websocket_endpoint
    await websocket_endpoint(websocket)


def stream_generator():
    delay = 1.0 / max(1, STREAM_FPS)
    while True:
        pipeline = _active_pipeline
        jpeg = pipeline.get_frame_jpeg() if pipeline is not None else None
        if jpeg is None:
            label = "Backend not ready" if pipeline is None else "No camera signal"
            jpeg = _blank_frame(label)
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n"
        time.sleep(delay)


def _blank_frame(text: str) -> bytes:
    import numpy as np
    frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
    cv2.putText(
        frame,
        text,
        (50, FRAME_HEIGHT // 2),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (180, 180, 180),
        2,
    )
    ret, jpeg = cv2.imencode(".jpg", frame)
    return jpeg.tobytes() if ret else b""


@app.get("/api/stream")
def video_stream():
    return StreamingResponse(
        stream_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.get("/api/stream/frame")
def video_frame():
    pipeline = _active_pipeline
    if pipeline is None:
        return Response(content=_blank_frame("Backend not ready"), media_type="image/jpeg")

    jpeg = pipeline.get_frame_jpeg()
    if jpeg is None:
        jpeg = _blank_frame("No camera signal")

    return Response(
        content=jpeg,
        media_type="image/jpeg",
        headers={"Cache-Control": "no-store"},
    )


if (_FRONTEND_DIST / "assets").is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=_FRONTEND_DIST / "assets"),
        name="frontend-assets",
    )


@app.get("/", include_in_schema=False)
def frontend_index():
    index = _FRONTEND_DIST / "index.html"
    if index.is_file():
        return FileResponse(index)
    return {
        "name": "ErgoVision",
        "status": "backend ready",
        "ui": "Run npm run dev in frontend, or build the frontend for single-server mode.",
    }


@app.get("/{full_path:path}", include_in_schema=False)
def frontend_fallback(full_path: str):
    if full_path.startswith(("api/", "health", "ws/")):
        raise HTTPException(status_code=404)

    candidate = (_FRONTEND_DIST / full_path).resolve()
    if _FRONTEND_DIST in candidate.parents and candidate.is_file():
        return FileResponse(candidate)

    index = _FRONTEND_DIST / "index.html"
    if index.is_file():
        return FileResponse(index)

    raise HTTPException(status_code=404)
