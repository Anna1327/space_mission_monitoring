from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ...utils.websocket_manager import ws_manager
import json

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{system_id}")
async def websocket_endpoint(websocket: WebSocket, system_id: int):
    await websocket.accept()
    await ws_manager.subscribe(system_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                command = message.get("command")

                if command == "ping":
                    await websocket.send_text(json.dumps({"status": "pong"}))
                elif command == "get_system_id":
                    await websocket.send_text(json.dumps({"system_id": system_id}))
                else:
                    await websocket.send_text(json.dumps({"error": f"Unknown command: {command}"}))
            except json.JSONDecodeError:
                await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        await ws_manager.unsubscribe(system_id, websocket)
