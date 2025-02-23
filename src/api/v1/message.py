from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.core.di.services import get_message_service
from src.core.di.user import CurrentUser
from src.schemas.message import (
    MessageInfo,
    ChatHistoryRequest,
)
from src.services.message import MessageService

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.get("/history/{chat_id}")
async def get_chat_history(
    chat_id: UUID,
    current_user: CurrentUser,
    params: Annotated[ChatHistoryRequest, Depends()],
    service: Annotated[MessageService, Depends(get_message_service)],
) -> list[MessageInfo]:
    return await service.get_chat_history(chat_id, params, current_user)
