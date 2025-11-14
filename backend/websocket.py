"""
WebSocket Module for RAIA Enterprise
=====================================

Provides real-time updates via WebSocket for:
- Live metrics updates
- Run progress tracking
- Dashboard real-time data
- Alerts and notifications
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Set
import json
import asyncio
from datetime import datetime
import uuid

# ============================================================================
# Connection Manager
# ============================================================================

class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        # All active connections
        self.active_connections: List[WebSocket] = []

        # Connections by channel (topic-based subscriptions)
        self.channels: Dict[str, Set[WebSocket]] = {}

        # Connection metadata
        self.connection_info: Dict[WebSocket, Dict] = {}

    async def connect(self, websocket: WebSocket, user_id: str = None):
        """
        Accept new WebSocket connection.

        Args:
            websocket: WebSocket connection
            user_id: Optional user identifier
        """
        await websocket.accept()
        self.active_connections.append(websocket)

        # Store connection metadata
        self.connection_info[websocket] = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            "subscriptions": set()
        }

        print(f"✅ WebSocket connected: {self.connection_info[websocket]['id']}")

    def disconnect(self, websocket: WebSocket):
        """
        Remove WebSocket connection.

        Args:
            websocket: WebSocket connection to remove
        """
        # Remove from active connections
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        # Remove from all channels
        for channel in self.channels.values():
            if websocket in channel:
                channel.remove(websocket)

        # Remove metadata
        if websocket in self.connection_info:
            conn_id = self.connection_info[websocket]["id"]
            del self.connection_info[websocket]
            print(f"❌ WebSocket disconnected: {conn_id}")

    async def subscribe(self, websocket: WebSocket, channel: str):
        """
        Subscribe connection to a channel.

        Args:
            websocket: WebSocket connection
            channel: Channel name to subscribe to
        """
        if channel not in self.channels:
            self.channels[channel] = set()

        self.channels[channel].add(websocket)

        if websocket in self.connection_info:
            self.connection_info[websocket]["subscriptions"].add(channel)

        print(f"📡 Subscribed to channel: {channel}")

    async def unsubscribe(self, websocket: WebSocket, channel: str):
        """
        Unsubscribe connection from a channel.

        Args:
            websocket: WebSocket connection
            channel: Channel name to unsubscribe from
        """
        if channel in self.channels and websocket in self.channels[channel]:
            self.channels[channel].remove(websocket)

        if websocket in self.connection_info:
            self.connection_info[websocket]["subscriptions"].discard(channel)

        print(f"🔇 Unsubscribed from channel: {channel}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send message to specific connection.

        Args:
            message: Message to send
            websocket: Target WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: dict):
        """
        Broadcast message to all connections.

        Args:
            message: Message to broadcast
        """
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting: {e}")
                disconnected.append(connection)

        # Clean up disconnected
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_to_channel(self, message: dict, channel: str):
        """
        Broadcast message to specific channel.

        Args:
            message: Message to broadcast
            channel: Target channel name
        """
        if channel not in self.channels:
            return

        disconnected = []

        for connection in self.channels[channel]:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to channel {channel}: {e}")
                disconnected.append(connection)

        # Clean up disconnected
        for connection in disconnected:
            self.disconnect(connection)

    def get_stats(self) -> dict:
        """Get connection statistics."""
        return {
            "total_connections": len(self.active_connections),
            "channels": {
                channel: len(connections)
                for channel, connections in self.channels.items()
            },
            "connections": [
                {
                    "id": info["id"],
                    "user_id": info.get("user_id"),
                    "connected_at": info["connected_at"].isoformat(),
                    "subscriptions": list(info["subscriptions"])
                }
                for info in self.connection_info.values()
            ]
        }


# Global connection manager
manager = ConnectionManager()


# ============================================================================
# Message Types
# ============================================================================

class MessageType:
    """WebSocket message types."""

    # System messages
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"

    # Subscription messages
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"

    # Data messages
    METRIC_UPDATE = "metric_update"
    RUN_UPDATE = "run_update"
    ALERT = "alert"
    NOTIFICATION = "notification"

    # Dashboard messages
    DASHBOARD_UPDATE = "dashboard_update"
    RETRIEVAL_UPDATE = "retrieval_update"
    QUALITY_UPDATE = "quality_update"


# ============================================================================
# Event Emitters
# ============================================================================

class WebSocketEmitter:
    """Emit events to WebSocket clients."""

    @staticmethod
    async def emit_metric_update(metrics: dict, channel: str = "metrics"):
        """
        Emit metrics update.

        Args:
            metrics: Metrics data
            channel: Target channel
        """
        message = {
            "type": MessageType.METRIC_UPDATE,
            "timestamp": datetime.utcnow().isoformat(),
            "data": metrics
        }
        await manager.broadcast_to_channel(message, channel)

    @staticmethod
    async def emit_run_update(run_id: str, status: str, progress: float = None):
        """
        Emit run progress update.

        Args:
            run_id: Run identifier
            status: Run status
            progress: Progress percentage (0-100)
        """
        message = {
            "type": MessageType.RUN_UPDATE,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "run_id": run_id,
                "status": status,
                "progress": progress
            }
        }
        await manager.broadcast_to_channel(message, f"run:{run_id}")
        await manager.broadcast_to_channel(message, "runs")

    @staticmethod
    async def emit_alert(
        level: str,
        title: str,
        message: str,
        details: dict = None
    ):
        """
        Emit alert notification.

        Args:
            level: Alert level (info, warning, error, critical)
            title: Alert title
            message: Alert message
            details: Additional details
        """
        alert = {
            "type": MessageType.ALERT,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "level": level,
                "title": title,
                "message": message,
                "details": details or {}
            }
        }
        await manager.broadcast_to_channel(alert, "alerts")

    @staticmethod
    async def emit_dashboard_update(summary: dict):
        """
        Emit dashboard summary update.

        Args:
            summary: Dashboard summary data
        """
        message = {
            "type": MessageType.DASHBOARD_UPDATE,
            "timestamp": datetime.utcnow().isoformat(),
            "data": summary
        }
        await manager.broadcast_to_channel(message, "dashboard")

    @staticmethod
    async def emit_retrieval_update(metrics: dict):
        """
        Emit retrieval metrics update.

        Args:
            metrics: Retrieval metrics
        """
        message = {
            "type": MessageType.RETRIEVAL_UPDATE,
            "timestamp": datetime.utcnow().isoformat(),
            "data": metrics
        }
        await manager.broadcast_to_channel(message, "retrieval")

    @staticmethod
    async def emit_quality_update(metrics: dict):
        """
        Emit quality metrics update.

        Args:
            metrics: Quality metrics
        """
        message = {
            "type": MessageType.QUALITY_UPDATE,
            "timestamp": datetime.utcnow().isoformat(),
            "data": metrics
        }
        await manager.broadcast_to_channel(message, "quality")


# ============================================================================
# Background Tasks
# ============================================================================

class MetricsStreamer:
    """Stream metrics updates at regular intervals."""

    def __init__(self, interval: int = 5):
        """
        Initialize metrics streamer.

        Args:
            interval: Update interval in seconds
        """
        self.interval = interval
        self.running = False
        self.task = None

    async def start(self):
        """Start streaming metrics."""
        self.running = True
        self.task = asyncio.create_task(self._stream())
        print(f"📊 Started metrics streaming (interval: {self.interval}s)")

    async def stop(self):
        """Stop streaming metrics."""
        self.running = False
        if self.task:
            self.task.cancel()
        print("⏹️  Stopped metrics streaming")

    async def _stream(self):
        """Internal streaming loop."""
        while self.running:
            try:
                # Fetch latest metrics
                metrics = await self._fetch_metrics()

                # Emit to subscribers
                await WebSocketEmitter.emit_dashboard_update(metrics)

                # Wait for next interval
                await asyncio.sleep(self.interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error streaming metrics: {e}")
                await asyncio.sleep(self.interval)

    async def _fetch_metrics(self) -> dict:
        """Fetch latest metrics from database."""
        # This would query your database
        # For now, return sample data
        return {
            "total_runs": 150,
            "avg_precision": 0.85,
            "avg_recall": 0.78,
            "avg_latency_ms": 145.5,
            "cache_hit_rate": 92.0
        }


# Global metrics streamer
metrics_streamer = MetricsStreamer(interval=5)


# ============================================================================
# WebSocket Handler
# ============================================================================

async def websocket_handler(websocket: WebSocket, user_id: str = None):
    """
    Main WebSocket handler.

    Args:
        websocket: WebSocket connection
        user_id: Optional authenticated user ID
    """
    await manager.connect(websocket, user_id)

    try:
        # Send welcome message
        await websocket.send_json({
            "type": MessageType.CONNECTED,
            "message": "Connected to RAIA WebSocket",
            "connection_id": manager.connection_info[websocket]["id"]
        })

        # Handle messages
        while True:
            # Receive message
            data = await websocket.receive_json()
            message_type = data.get("type")

            # Handle subscription
            if message_type == MessageType.SUBSCRIBE:
                channel = data.get("channel")
                if channel:
                    await manager.subscribe(websocket, channel)
                    await websocket.send_json({
                        "type": "subscribed",
                        "channel": channel
                    })

            # Handle unsubscription
            elif message_type == MessageType.UNSUBSCRIBE:
                channel = data.get("channel")
                if channel:
                    await manager.unsubscribe(websocket, channel)
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "channel": channel
                    })

            # Echo for testing
            elif message_type == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })

            else:
                await websocket.send_json({
                    "type": MessageType.ERROR,
                    "message": f"Unknown message type: {message_type}"
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)

    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# ============================================================================
# Usage Examples
# ============================================================================

"""
Example usage in FastAPI main.py:

```python
from fastapi import FastAPI, WebSocket
from backend.websocket import websocket_handler, metrics_streamer

app = FastAPI()

@app.on_event("startup")
async def startup():
    await metrics_streamer.start()

@app.on_event("shutdown")
async def shutdown():
    await metrics_streamer.stop()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_handler(websocket)

@app.websocket("/ws/{user_id}")
async def websocket_user_endpoint(websocket: WebSocket, user_id: str):
    await websocket_handler(websocket, user_id)
```

Example client usage (JavaScript):

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

// Handle connection
ws.onopen = () => {
  console.log('Connected to RAIA WebSocket');

  // Subscribe to channels
  ws.send(JSON.stringify({
    type: 'subscribe',
    channel: 'dashboard'
  }));

  ws.send(JSON.stringify({
    type: 'subscribe',
    channel: 'alerts'
  }));
};

// Handle messages
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  switch(message.type) {
    case 'dashboard_update':
      updateDashboard(message.data);
      break;
    case 'alert':
      showAlert(message.data);
      break;
    case 'metric_update':
      updateMetrics(message.data);
      break;
  }
};

// Handle errors
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

// Handle disconnection
ws.onclose = () => {
  console.log('Disconnected from WebSocket');
  // Implement reconnection logic
};
```
"""

if __name__ == "__main__":
    # Test
    import asyncio

    async def test():
        # Start metrics streaming
        await metrics_streamer.start()

        # Simulate some events
        await WebSocketEmitter.emit_alert(
            "info",
            "Test Alert",
            "This is a test alert"
        )

        await asyncio.sleep(2)

        await WebSocketEmitter.emit_run_update(
            "run_123",
            "in_progress",
            progress=45.0
        )

        await asyncio.sleep(10)

        # Stop streaming
        await metrics_streamer.stop()

    asyncio.run(test())
