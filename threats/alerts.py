# from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# from starlette.websockets import WebSocketState
# from typing import List
# import json
#
# router = APIRouter()
# connected_clients: List[WebSocket] = []
#
#
# @router.websocket("/ws/alerts")
# async def alert_stream(websocket: WebSocket):
#     await websocket.accept()
#     connected_clients.append(websocket)
#     try:
#         while True:
#             if websocket.client_state != WebSocketState.CONNECTED:
#                 break
#             await websocket.receive_text()  # Keeps the socket alive
#     except WebSocketDisconnect:
#         if websocket in connected_clients:
#             connected_clients.remove(websocket)
#
#
# async def broadcast_alert(alert: dict):
#     for client in connected_clients:
#         if client.client_state == WebSocketState.CONNECTED:
#             await client.send_text(json.dumps(alert))
