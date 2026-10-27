import asyncio
import os
import threading
from collections import defaultdict
from http.cookies import SimpleCookie
from typing import Any
from urllib.parse import unquote

import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from backend.config.logging_setting import setup_logger

load_dotenv()

router = APIRouter()
logger = setup_logger("vm_events")

AUTHJWT_SECRET_KEY = os.getenv("AUTHJWT_SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_COOKIE_KEY = os.getenv("AUTHJWT_ACCESS_COOKIE_KEY", "access_token_cookie")


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        async with self._lock:
            connections = list(self._connections)

        stale: list[WebSocket] = []
        for ws in connections:
            try:
                await ws.send_json(message)
            except Exception:
                stale.append(ws)

        if stale:
            async with self._lock:
                for ws in stale:
                    self._connections.discard(ws)


manager = ConnectionManager()
_vm_locks: dict[str, threading.Lock] = defaultdict(threading.Lock)


def normalize_vm_state(state: str) -> str:
    return " ".join(state.strip().lower().split())


def acquire_vm_lock(vm_name: str) -> bool:
    lock = _vm_locks[vm_name]
    return lock.acquire(blocking=False)


def release_vm_lock(vm_name: str) -> None:
    lock = _vm_locks.get(vm_name)
    if lock and lock.locked():
        lock.release()


def publish_event(event: dict[str, Any]) -> None:
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(manager.broadcast(event))
    except RuntimeError:
        asyncio.run(manager.broadcast(event))


def _extract_cookie_token(cookie_header: str | None) -> str | None:
    if not cookie_header:
        return None
    cookie = SimpleCookie()
    cookie.load(cookie_header)
    morsel = cookie.get(ACCESS_COOKIE_KEY)
    if not morsel:
        return None
    return unquote(morsel.value)


def _decode_token(token: str) -> dict[str, Any] | None:
    if not token:
        return None
    try:
        return jwt.decode(token, AUTHJWT_SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        return None


@router.websocket("/ws/vm-updates")
async def vm_updates(websocket: WebSocket, token: str = Query(default="")):
    bearer_token = token or _extract_cookie_token(websocket.headers.get("cookie"))
    claims = _decode_token(bearer_token or "")

    if claims is None:
        await websocket.close(code=4401)
        return

    await manager.connect(websocket)
    await websocket.send_json({"event": "connected", "username": claims.get("sub", "unknown")})

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception:
        logger.exception("Unexpected websocket error")
        await manager.disconnect(websocket)
