from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.chat import ChatMember


class ChatMemberRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, chat_member: ChatMember) -> ChatMember:
        self._session.add(chat_member)
        return chat_member

    async def create_many(self, chat_members: list[ChatMember]) -> list[ChatMember]:
        self._session.add_all(chat_members)
        return chat_members

    async def delete_members(self, chat_id: UUID, user_ids: list[UUID]) -> None:
        stmt = delete(ChatMember).where(
            ChatMember.chat_id == chat_id, ChatMember.user_id.in_(user_ids)
        )
        await self._session.execute(stmt)
