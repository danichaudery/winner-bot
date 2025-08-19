from __future__ import annotations

from typing import Dict, Set, Any, Callable
from fastapi import WebSocket
import asyncio


class WebSocketManager:
    def __init__(self) -> None:
        self.topics: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, topic: str) -> None:
        await websocket.accept()
        async with self._lock:
            self.topics.setdefault(topic, set()).add(websocket)

    async def disconnect(self, websocket: WebSocket, topic: str) -> None:
        async with self._lock:
            conns = self.topics.get(topic)
            if conns and websocket in conns:
                conns.remove(websocket)
            if conns is not None and len(conns) == 0:
                self.topics.pop(topic, None)

    async def broadcast(self, topic: str, message: dict[str, Any]) -> None:
        conns = list(self.topics.get(topic, set()))
        for ws in conns:
            try:
                await ws.send_json(message)
            except Exception:
                # best-effort; drop on error
                await self.disconnect(ws, topic)

