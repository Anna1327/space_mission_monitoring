from fastapi import WebSocket
from typing import List, Dict, Any
import asyncio
import json


class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        if not self.active_connections:
            return

        data = json.dumps(message)
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(data)
            except Exception:
                disconnected.append(connection)

        async with self._lock:
            for conn in disconnected:
                if conn in self.active_connections:
                    self.active_connections.remove(conn)

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


ws_manager = WebSocketManager()
