import asyncio
import logging

from fastapi import WebSocket, WebSocketDisconnect

from ..config import WEBSOCKET_UPDATE_INTERVAL

logger = logging.getLogger(__name__)

active_connections: set[WebSocket] = set()


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        from ..main import get_pipeline
        while True:
            pipeline = get_pipeline()
            if pipeline is not None:
                await websocket.send_json(pipeline.get_current())
            await asyncio.sleep(WEBSOCKET_UPDATE_INTERVAL)
    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("WebSocket error")
    finally:
        active_connections.discard(websocket)


async def broadcast(event: dict):
    if not active_connections:
        return
    for ws in list(active_connections):
        try:
            await ws.send_json(event)
        except Exception:
            active_connections.discard(ws)
