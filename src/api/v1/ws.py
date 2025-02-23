from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from fastapi.security import HTTPBearer

from src.core.di.services import (
    get_message_service,
    get_chat_service,
    get_token_service,
)
from src.core.di.repositories import get_user_repository
from src.repositories.user import UserRepository
from src.services.message import MessageService
from src.services.chat import ChatService
from src.services.token import TokenService
from src.services.websocket.handler import WebSocketHandler
from src.services.websocket.manager import connection_manager

router = APIRouter()
security = HTTPBearer()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str | None = None,
    message_service: Annotated[MessageService, Depends(get_message_service)] = None,
    chat_service: Annotated[ChatService, Depends(get_chat_service)] = None,
    token_service: Annotated[TokenService, Depends(get_token_service)] = None,
    user_repository: Annotated[UserRepository, Depends(get_user_repository)] = None,
) -> None:
    if not token:
        await websocket.close(code=4001, reason="Отсутствует токен")
        return

    try:
        user_id = token_service.decode_token(token)
        user = await user_repository.get_by_id(user_id)
        if not user:
            await websocket.close(code=4001, reason="Неверный токен")
            return

        connection_id = str(uuid4())
        await connection_manager.connect(websocket, user, connection_id)

        handler = WebSocketHandler(
            websocket=websocket,
            user=user,
            connection_id=connection_id,
            message_service=message_service,
            chat_service=chat_service,
        )

        try:
            while True:
                message = await websocket.receive_text()
                await handler.handle_message(message)

        except WebSocketDisconnect:
            await connection_manager.disconnect(user.id, connection_id)

    except Exception as e:  # noqa: BLE001
        print(e, type(e))
        await websocket.close(code=4000, reason=str(e))
