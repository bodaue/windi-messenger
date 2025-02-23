from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import (
    UserNotFoundException,
    ChatAlreadyExistsException,
    InvalidChatParticipantException,
)
from src.models.chat import Chat, ChatMember, ChatType
from src.models.user import User
from src.repositories.chat import ChatRepository
from src.repositories.chat_member import ChatMemberRepository
from src.repositories.user import UserRepository
from src.schemas.chat import ChatCreate, ChatInfo


class ChatService:
    def __init__(
        self,
        session: AsyncSession,
        chat_repository: ChatRepository,
        chat_member_repository: ChatMemberRepository,
        user_repository: UserRepository,
    ) -> None:
        self._session = session
        self._chat_repository = chat_repository
        self._chat_member_repository = chat_member_repository
        self._user_repository = user_repository

    async def create_personal_chat(
        self,
        data: ChatCreate,
        current_user: User,
    ) -> ChatInfo:
        if data.user_id == current_user.id:
            raise InvalidChatParticipantException

        other_user = await self._user_repository.get_by_id(data.user_id)
        if not other_user:
            raise UserNotFoundException

        existing_chat = await self._chat_repository.find_personal_chat_between_users(
            current_user.id,
            other_user.id,
        )
        if existing_chat:
            raise ChatAlreadyExistsException

        chat = Chat(
            name=f"Чат {current_user.name} и {other_user.name}",
            type=ChatType.PERSONAL,
        )
        await self._chat_repository.create(chat)

        members = [
            ChatMember(chat=chat, user=current_user),
            ChatMember(chat=chat, user=other_user),
        ]
        await self._chat_member_repository.create_many(members)

        await self._session.commit()
        return ChatInfo.model_validate(chat)

    async def get_user_chats(self, user: User) -> list[ChatInfo]:
        chats = await self._chat_repository.get_user_chats(user.id)
        return [ChatInfo.model_validate(chat) for chat in chats]

    async def get_chat_access(self, chat_id: UUID, user: User) -> Chat | None:
        chat = await self._chat_repository.get_by_id(chat_id)
        if not chat:
            return None

        if any(member.user_id == user.id for member in chat.members):
            return chat

        return None
