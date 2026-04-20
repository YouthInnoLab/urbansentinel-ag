from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI(title="UrbanSentinel API Broker")

# Allow CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=[\"*\"],
    allow_credentials=True,
    allow_methods=[\"*\"],
    allow_headers=[\"*\"],
)

# Connection manager to track open WebSockets
class ConnectionManager:
    def __init__(self):
        self.dashboard_connections: list[WebSocket] = []

    async def connect_dashboard(self, websocket: WebSocket):
        await websocket.accept()
        self.dashboard_connections.append(websocket)
        print("Dashboard connected.")

    def disconnect_dashboard(self, websocket: WebSocket):
        if websocket in self.dashboard_connections:
            self.dashboard_connections.remove(websocket)
            print("Dashboard disconnected.")

    async def broadcast_alert(self, alert_data: str):
        for connection in self.dashboard_connections:
            try:
                await connection.send_text(alert_data)
            except Exception as e:
                print(f"Error broadcasting to dashboard: {e}")

manager = ConnectionManager()

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """
    WebSocket endpoint for the front-end dashboard to receive live alerts.
    """
    await manager.connect_dashboard(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_dashboard(websocket)

@app.websocket("/ws/edge")
async def websocket_edge(websocket: WebSocket):
    """
    WebSocket endpoint for Edge Nodes to publish detected anomalies.
    """
    await websocket.accept()
    try:
        while True:
            # Receive alert from edge node
            data = await websocket.receive_text()
            print(f"Received alert from EDGE NODE: {data}")
            # Immediately broadcast down to the dispatch dashboard
            await manager.broadcast_alert(data)
    except WebSocketDisconnect:
        print("An Edge Node disconnected.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
