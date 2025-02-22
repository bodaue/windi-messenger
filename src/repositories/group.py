from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Group, GroupMember


class GroupRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, group: Group) -> Group:
        self._session.add(group)
        return group

    async def get_by_id(self, group_id: UUID) -> Group | None:
        stmt = (
            select(Group)
            .where(Group.id == group_id)
            .options(
                selectinload(Group.creator),
                selectinload(Group.members).selectinload(GroupMember.user),
                selectinload(Group.chat),
            )
        )
        return await self._session.scalar(stmt)

    async def delete(self, group_id: UUID) -> None:
        stmt = delete(Group).where(Group.id == group_id)
        await self._session.execute(stmt)
