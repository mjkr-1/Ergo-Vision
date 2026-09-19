from __future__ import annotations

import logging
from pathlib import Path
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

MODEL_URLS = {
    "face_landmarker.task": "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task",
    "pose_landmarker_lite.task": "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task",
}

MIN_MODEL_BYTES = 100_000


def ensure_models(auto_download: bool = True) -> bool:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    missing = [name for name in MODEL_URLS if not _is_valid_model(MODELS_DIR / name)]
    if not missing:
        return True

    if not auto_download:
        logger.error("MediaPipe model files are missing: %s", ", ".join(missing))
        return False

    for name in missing:
        if not _download_model(name, MODEL_URLS[name]):
            return False

    return all(_is_valid_model(MODELS_DIR / name) for name in MODEL_URLS)


def _is_valid_model(path: Path) -> bool:
    return path.exists() and path.is_file() and path.stat().st_size >= MIN_MODEL_BYTES


def _download_model(name: str, url: str) -> bool:
    target = MODELS_DIR / name
    temp = target.with_suffix(target.suffix + ".download")
    try:
        logger.info("Downloading MediaPipe model %s", name)
        request = Request(url, headers={"User-Agent": "ErgoVision/1.0"})
        with urlopen(request, timeout=60) as response, temp.open("wb") as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)

        if not _is_valid_model(temp):
            raise RuntimeError(f"Downloaded model {name} is unexpectedly small")

        temp.replace(target)
        logger.info("Model ready: %s", target)
        return True
    except Exception as exc:
        temp.unlink(missing_ok=True)
        logger.error("Could not download %s: %s", name, exc)
        return False


if __name__ == "__main__":
    raise SystemExit(0 if ensure_models(auto_download=True) else 1)
