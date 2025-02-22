from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import ChatNotFoundException, MessageNotFoundException
from src.models.message import Message
from src.models.user import User
from src.repositories.chat import ChatRepository
from src.repositories.message import MessageRepository
from src.repositories.message_read_state import MessageReadStateRepository
from src.schemas.message import (
    MessageCreate,
    MessageInfo,
    ChatHistoryRequest,
    MessageRead,
)


class MessageService:
    def __init__(
        self,
        session: AsyncSession,
        message_repository: MessageRepository,
        message_read_state_repository: MessageReadStateRepository,
        chat_repository: ChatRepository,
    ) -> None:
        self._session = session
        self._message_repository = message_repository
        self._message_read_state_repository = message_read_state_repository
        self._chat_repository = chat_repository

    async def create_message(
        self,
        data: MessageCreate,
        sender: User,
    ) -> MessageInfo:
        chat = await self._chat_repository.get_by_id(data.chat_id)
        if not chat:
            raise ChatNotFoundException

        if not any(member.user_id == sender.id for member in chat.members):
            raise ChatNotFoundException

        message = Message(
            chat_id=data.chat_id,
            sender_id=sender.id,
            text=data.text,
        )
        await self._message_repository.create(message)

        await self._message_read_state_repository.mark_as_read(
            message_id=message.id, user_id=sender.id
        )
        await self._session.commit()
        return MessageInfo.model_validate(message)

    async def mark_as_read(
        self,
        data: MessageRead,
        current_user: User,
    ) -> None:
        message = await self._message_repository.get_by_id(data.message_id)
        if not message:
            raise MessageNotFoundException

        await self._message_read_state_repository.mark_as_read(
            message_id=data.message_id, user_id=current_user.id
        )
        await self._session.commit()

    async def get_chat_history(
        self,
        chat_id: UUID,
        params: ChatHistoryRequest,
        current_user: User,
    ) -> list[MessageInfo]:
        chat = await self._chat_repository.get_by_id(chat_id)
        if not chat or not any(
            member.user_id == current_user.id for member in chat.members
        ):
            raise ChatNotFoundException

        messages = await self._message_repository.get_chat_history(
            chat_id=chat_id,
            limit=params.limit,
            offset=params.offset,
        )

        return [MessageInfo.model_validate(message) for message in messages]
