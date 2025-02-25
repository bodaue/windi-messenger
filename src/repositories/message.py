from uuid import UUID

from sqlalchemy import select, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.message import Message


class MessageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, message: Message) -> Message:
        self._session.add(message)
        return message

    async def get_by_id(self, message_id: UUID) -> Message | None:
        stmt = (
            select(Message)
            .where(Message.id == message_id)
            .options(
                selectinload(Message.sender),
                selectinload(Message.read_states),
            )
        )
        return await self._session.scalar(stmt)

    async def get_chat_history(
        self,
        chat_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .options(
                selectinload(Message.sender),
                selectinload(Message.read_states),
            )
            .order_by(asc(Message.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.scalars(stmt)
        return list(result)

    async def find_by_idempotency_key(
        self, sender_id: UUID, idempotency_key: str
    ) -> Message | None:
        stmt = (
            select(Message)
            .where(
                Message.sender_id == sender_id,
                Message.idempotency_key == idempotency_key,
            )
            .options(
                selectinload(Message.sender),
                selectinload(Message.read_states),
            )
        )
        return await self._session.scalar(stmt)
