import json
from typing import Any

from fastapi import WebSocket

from src.exceptions import ApplicationException
from src.models import User
from src.schemas.message import MessageCreate
from src.schemas.websocket import (
    WebSocketAction,
    WSJoinChat,
    WSLeaveChat,
    WSSendMessage,
    WSMessageRead,
    WSTyping,
)
from src.services.chat import ChatService
from src.services.message import MessageService
from src.services.websocket.manager import connection_manager


class WebSocketHandler:
    """Обработчик WebSocket сообщений."""

    def __init__(
        self,
        websocket: WebSocket,
        user: User,
        connection_id: str,
        message_service: MessageService,
        chat_service: ChatService,
    ) -> None:
        self.websocket = websocket
        self.user = user
        self.connection_id = connection_id
        self.message_service = message_service
        self.chat_service = chat_service

    async def handle_message(self, raw_data: str) -> None:
        """Обработка входящего сообщения."""
        try:
            data = json.loads(raw_data)
            print(data)
            action = data.get("action")

            handlers = {
                WebSocketAction.JOIN_CHAT: self._handle_join_chat,
                WebSocketAction.LEAVE_CHAT: self._handle_leave_chat,
                WebSocketAction.SEND_MESSAGE: self._handle_send_message,
                WebSocketAction.MESSAGE_READ: self._handle_message_read,
                WebSocketAction.TYPING: self._handle_typing,
            }
            print(action)
            handler = handlers.get(action)
            if handler:
                await handler(data)
            else:
                await self._send_error("Неизвестное действие")

        except json.JSONDecodeError:
            await self._send_error("Неверный формат JSON")
        except (ValueError, ApplicationException) as e:
            await self._send_error(str(e))

    async def _handle_join_chat(self, data: dict[str, Any]) -> None:
        """Обработка присоединения к чату."""
        msg = WSJoinChat.model_validate(data)
        chat = await self.chat_service.get_chat_access(msg.chat_id, self.user)

        if chat:
            connection_manager.join_chat(self.user.id, msg.chat_id)
            await self._send_success("joined", {"chat_id": str(msg.chat_id)})

    async def _handle_leave_chat(self, data: dict[str, Any]) -> None:
        """Обработка выхода из чата."""
        msg = WSLeaveChat.model_validate(data)
        connection_manager.leave_chat(self.user.id, msg.chat_id)
        await self._send_success("left", {"chat_id": str(msg.chat_id)})

    async def _handle_send_message(self, data: dict[str, Any]) -> None:
        """Обработка отправки сообщения."""
        msg = WSSendMessage.model_validate(data)
        message_data = MessageCreate(
            chat_id=msg.chat_id, text=msg.text, idempotency_key=msg.idempotency_key
        )
        message = await self.message_service.create_message(message_data, self.user)

        await connection_manager.broadcast_message(
            msg.chat_id,
            {"event": "new_message", "data": message.model_dump(mode="json")},
        )

    async def _handle_message_read(self, data: dict[str, Any]) -> None:
        """Обработка прочтения сообщения."""
        msg = WSMessageRead.model_validate(data)
        read_message = await self.message_service.mark_as_read(msg, self.user)

        await connection_manager.notify_message_read(
            msg.chat_id,
            msg.message_id,
            self.user.id,
            read_message.read_at.isoformat(),
        )

    async def _handle_typing(self, data: dict[str, Any]) -> None:
        """Обработка события печатания."""
        msg = WSTyping.model_validate(data)
        # Проверяем доступ к чату
        chat = await self.chat_service.get_chat_access(msg.chat_id, self.user)

        if chat:
            # Оповещаем других участников чата
            await connection_manager.broadcast_message(
                msg.chat_id,
                {
                    "event": "typing",
                    "chat_id": str(msg.chat_id),
                    "user_name": self.user.name,
                },
                exclude_user=self.user.id,
            )

    async def _send_error(self, message: str) -> None:
        """Отправка сообщения об ошибке."""
        await self.websocket.send_json({"error": message})

    async def _send_success(self, status: str, data: dict[str, Any]) -> None:
        """Отправка успешного результата."""
        response = {"status": status, **data}
        await self.websocket.send_json(response)
