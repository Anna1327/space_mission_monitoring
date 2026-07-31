from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from websockets.exceptions import ConnectionClosed
import json


class WebSocketManager:
    def __init__(self):
        self.subscriptions = {}

    async def subscribe(self, system_id: int, websocket: WebSocket):
        sys_id_str = str(system_id)
        if sys_id_str not in self.subscriptions:
            self.subscriptions[sys_id_str] = []
        self.subscriptions[sys_id_str].append(websocket)

    async def unsubscribe(self, system_id: int, websocket: WebSocket):
        sys_id_str = str(system_id)
        if sys_id_str in self.subscriptions:
            if websocket in self.subscriptions[sys_id_str]:
                self.subscriptions[sys_id_str].remove(websocket)

    async def broadcast_to_system(self, system_id: int, message: dict):
        sys_id_str = str(system_id)
        if sys_id_str not in self.subscriptions:
            return
        data = json.dumps(message)

        for connection in self.subscriptions[sys_id_str]:
            try:
                await connection.send_text(data)
            except (WebSocketDisconnect, ConnectionClosed, RuntimeError):
                await self.unsubscribe(system_id, connection)


ws_manager = WebSocketManager()
