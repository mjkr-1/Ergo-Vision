import asyncio
import json
import logging

from fastapi import WebSocket, WebSocketDisconnect

from ..pipeline import PosturePipeline

logger = logging.getLogger(__name__)

active_connections: set[WebSocket] = set()


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        from ..main import get_pipeline
        pipeline = get_pipeline()
        while True:
            if pipeline is not None:
                event = pipeline.get_current()
                await websocket.send_text(json.dumps(event))
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        active_connections.discard(websocket)
    except Exception:
        active_connections.discard(websocket)
        logger.exception("WebSocket error")
    finally:
        active_connections.discard(websocket)


async def broadcast(event: dict):
    if not active_connections:
        return
    message = json.dumps(event)
    for ws in list(active_connections):
        try:
            await ws.send_text(message)
        except Exception:
            active_connections.discard(ws)