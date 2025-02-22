from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import GroupMember


class GroupMemberRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, member: GroupMember) -> None:
        self._session.add(member)

    async def create_many(self, members: list[GroupMember]) -> None:
        self._session.add_all(members)

    async def delete_members(self, group_id: UUID, user_ids: list[UUID]) -> None:
        stmt = delete(GroupMember).where(
            GroupMember.group_id == group_id, GroupMember.user_id.in_(user_ids)
        )
        await self._session.execute(stmt)
