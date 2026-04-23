from fastapi import WebSocket
from websockets.exceptions import ConnectionClosed
import json


class WebSocketManager:
    def __init__(self):
        self.subscriptions = {}

    async def subscribe(self, system_id: int, websocket: WebSocket):
        if system_id not in self.subscriptions:
            self.subscriptions[system_id] = []
        self.subscriptions[system_id].append(websocket)

    async def unsubscribe(self, system_id: int, websocket: WebSocket):
        if system_id in self.subscriptions:
            if websocket in self.subscriptions[system_id]:
                self.subscriptions[system_id].remove(websocket)

    async def broadcast_to_system(self, system_id: int, message: dict):
        if system_id not in self.subscriptions:
            return
        data = json.dumps(message)
        for connection in self.subscriptions[system_id]:
            try:
                await connection.send_text(data)
            except ConnectionClosed:
                await self.unsubscribe(system_id, connection)


ws_manager = WebSocketManager()

