from uuid import UUID

from fastapi import WebSocket

from src.models.user import User


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[UUID, set[WebSocket]] = {}
        self.connection_map: dict[WebSocket, User] = {}

    async def connect(
        self,
        websocket: WebSocket,
        chat_id: UUID,
        user: User,
    ) -> None:
        await websocket.accept()

        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = set()
        self.active_connections[chat_id].add(websocket)

        self.connection_map[websocket] = user

    async def disconnect(
        self,
        websocket: WebSocket,
        chat_id: UUID,
    ) -> None:
        if chat_id in self.active_connections:
            self.active_connections[chat_id].discard(websocket)
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]

        self.connection_map.pop(websocket, None)

    async def broadcast_to_chat(
        self,
        chat_id: UUID,
        message: dict,
        exclude: WebSocket | None = None,
    ) -> None:
        if chat_id in self.active_connections:
            for connection in self.active_connections[chat_id]:
                if connection != exclude:
                    await connection.send_json(message)

    def get_user_by_connection(self, websocket: WebSocket) -> User | None:
        return self.connection_map.get(websocket)
