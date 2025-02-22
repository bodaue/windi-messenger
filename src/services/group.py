from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import UserNotFoundException, GroupNotFoundException, AccessDenied
from src.models.chat import Chat, ChatType, ChatMember
from src.models.group import Group, GroupMember
from src.models.user import User
from src.repositories.chat import ChatRepository
from src.repositories.chat_member import ChatMemberRepository
from src.repositories.group import GroupRepository
from src.repositories.group_member import GroupMemberRepository
from src.repositories.user import UserRepository
from src.schemas.group import GroupCreate, GroupInfo, GroupMemberAdd, GroupMemberRemove


class GroupService:
    def __init__(
        self,
        session: AsyncSession,
        group_repository: GroupRepository,
        group_member_repository: GroupMemberRepository,
        user_repository: UserRepository,
        chat_repository: ChatRepository,
        chat_member_repository: ChatMemberRepository,
    ) -> None:
        self._session = session
        self._group_repository = group_repository
        self._group_member_repository = group_member_repository
        self._user_repository = user_repository
        self._chat_repository = chat_repository
        self._chat_member_repository = chat_member_repository

    async def create_group(self, data: GroupCreate, creator: User) -> GroupInfo:
        users = []
        if data.member_ids:
            for user_id in data.member_ids:
                user = await self._user_repository.get_by_id(user_id)
                if not user:
                    raise UserNotFoundException(f"User with id {user_id} not found")
                users.append(user)

        group = Group(title=data.title, creator=creator)
        await self._group_repository.create(group)

        members = [GroupMember(group=group, user=user) for user in users]
        members.append(GroupMember(group=group, user=creator))
        await self._group_member_repository.create_many(members)

        chat = Chat(name=data.title, type=ChatType.GROUP, group=group)
        await self._chat_repository.create(chat)

        chat_members = [ChatMember(chat=chat, user=user) for user in [*users, creator]]
        await self._chat_member_repository.create_many(chat_members)

        await self._session.commit()
        return GroupInfo.model_validate(group)

    async def get_group(self, group_id: UUID, current_user: User) -> GroupInfo:
        group = await self._get_group_with_access(
            group_id, current_user, creator_only=False
        )
        return GroupInfo.model_validate(group)

    async def add_members(
        self, group_id: UUID, data: GroupMemberAdd, current_user: User
    ) -> GroupInfo:
        group = await self._get_group_with_access(
            group_id, current_user, creator_only=True
        )

        chat = group.chat

        for user_id in data.user_ids:
            user = await self._user_repository.get_by_id(user_id)
            if not user:
                raise UserNotFoundException(f"User with id {user_id} not found")

            if not any(member.user_id == user.id for member in group.members):
                member = GroupMember(group=group, user=user)
                chat_member = ChatMember(chat=chat, user=user)
                await self._group_member_repository.create(member)
                await self._chat_member_repository.create(chat_member)

        await self._session.commit()
        return GroupInfo.model_validate(group)

    async def remove_members(
        self, group_id: UUID, data: GroupMemberRemove, current_user: User
    ) -> GroupInfo:
        group = await self._get_group_with_access(
            group_id, current_user, creator_only=True
        )
        if current_user.id in data.user_ids:
            raise AccessDenied("Cannot remove group creator")

        await self._group_member_repository.delete_members(group_id, data.user_ids)
        await self._chat_member_repository.delete_members(group.chat.id, data.user_ids)

        await self._session.commit()
        await self._session.refresh(group)
        return GroupInfo.model_validate(group)

    async def delete_group(self, group_id: UUID, current_user: User) -> None:
        await self._get_group_with_access(group_id, current_user, creator_only=True)
        await self._group_repository.delete(group_id)
        await self._session.commit()

    async def _get_group_with_access(
        self, group_id: UUID, user: User, creator_only: bool
    ) -> Group:
        group = await self._group_repository.get_by_id(group_id)
        if not group:
            raise GroupNotFoundException

        if creator_only and group.creator_id != user.id:
            raise AccessDenied("Access to group denied")

        if not creator_only and not any(
            member.user_id == user.id for member in group.members
        ):
            raise AccessDenied("Access to group denied")

        return group
