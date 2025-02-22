from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from src.core.di.services import get_chat_service
from src.core.di.user import CurrentUser
from src.schemas.chat import ChatCreate, ChatInfo
from src.services.chat import ChatService

router = APIRouter(prefix="/chats", tags=["chats"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_chat(
    data: ChatCreate,
    current_user: CurrentUser,
    service: Annotated[ChatService, Depends(get_chat_service)],
) -> ChatInfo:
    return await service.create_personal_chat(data, current_user)


@router.get("")
async def get_my_chats(
    current_user: CurrentUser,
    service: Annotated[ChatService, Depends(get_chat_service)],
) -> list[ChatInfo]:
    return await service.get_user_chats(current_user)
