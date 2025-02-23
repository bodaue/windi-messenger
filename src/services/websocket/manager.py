from collections import defaultdict
from typing import Any
from uuid import UUID

from fastapi import WebSocket

from src.models import User
from src.schemas.message import MessageInfo


class ConnectionManager:

    def __init__(self) -> None:
        self.active_connections: dict[UUID, dict[str, WebSocket]] = defaultdict(dict)
        self.user_chats: dict[UUID, set[UUID]] = defaultdict(set)

    async def connect(
        self, websocket: WebSocket, user: User, connection_id: str
    ) -> None:
        await websocket.accept()
        self.active_connections[user.id][connection_id] = websocket

    async def disconnect(self, user_id: UUID, connection_id: str) -> None:
        if user_id in self.active_connections:
            self.active_connections[user_id].pop(connection_id, None)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                self.user_chats.pop(user_id, None)

    def join_chat(self, user_id: UUID, chat_id: UUID) -> None:
        self.user_chats[user_id].add(chat_id)

    def leave_chat(self, user_id: UUID, chat_id: UUID) -> None:
        if user_id in self.user_chats:
            self.user_chats[user_id].discard(chat_id)
            if not self.user_chats[user_id]:
                self.user_chats.pop(user_id)

    async def broadcast_message(
        self,
        chat_id: UUID,
        message: MessageInfo | dict[str, Any],
        exclude_user: UUID | None = None,
    ) -> None:
        for user_id, chats in self.user_chats.items():
            if user_id != exclude_user and chat_id in chats:
                await self._send_to_user(user_id, message)

    async def notify_message_read(
        self, chat_id: UUID, message_id: UUID, user_id: UUID, read_at: str
    ) -> None:
        data = {
            "event": "message_read",
            "data": {
                "chat_id": str(chat_id),
                "message_id": str(message_id),
                "user_id": str(user_id),
                "read_at": read_at,
            },
        }
        await self.broadcast_message(chat_id, data)

    async def _send_to_user(
        self, user_id: UUID, message: MessageInfo | dict[str, Any]
    ) -> None:
        if user_id in self.active_connections:
            data = message.model_dump() if hasattr(message, "model_dump") else message
            for websocket in self.active_connections[user_id].values():
                await websocket.send_json(data)


# Глобальный экземпляр менеджера подключений
connection_manager = ConnectionManager()
