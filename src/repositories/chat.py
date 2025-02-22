from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Chat
from src.models.chat import ChatMember, ChatType


class ChatRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, chat: Chat) -> Chat:
        self._session.add(chat)
        return chat

    async def get_by_id(self, chat_id: UUID) -> Chat | None:
        return await self._session.get(Chat, chat_id)

    async def get_user_chats(self, user_id: UUID) -> Iterable[Chat]:
        stmt = (
            select(Chat)
            .join(ChatMember)
            .where(ChatMember.user_id == user_id)
            .options(
                selectinload(Chat.members).selectinload(ChatMember.user),
                selectinload(Chat.group),
            )
        )
        return (await self._session.scalars(stmt)).all()

    async def find_personal_chat_between_users(
        self,
        user1_id: UUID,
        user2_id: UUID,
    ) -> Chat | None:
        subq1 = (
            select(ChatMember.chat_id)
            .where(ChatMember.user_id == user1_id)
            .scalar_subquery()
        )
        subq2 = (
            select(ChatMember.chat_id)
            .where(ChatMember.user_id == user2_id)
            .scalar_subquery()
        )

        stmt = (
            select(Chat)
            .where(
                Chat.id.in_(subq1),
                Chat.id.in_(subq2),
                Chat.type == ChatType.PERSONAL,
            )
            .options(
                selectinload(Chat.members).selectinload(ChatMember.user),
            )
        )
        return await self._session.scalar(stmt)
