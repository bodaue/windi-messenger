from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.di.database import get_session
from src.repositories.chat import ChatRepository
from src.repositories.chat_member import ChatMemberRepository
from src.repositories.message import MessageRepository
from src.repositories.message_read_state import MessageReadStateRepository
from src.repositories.user import UserRepository


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    return UserRepository(session)


def get_chat_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ChatRepository:
    return ChatRepository(session)


def get_chat_member_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ChatMemberRepository:
    return ChatMemberRepository(session)


def get_message_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MessageRepository:
    return MessageRepository(session)


def get_message_read_state_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MessageReadStateRepository:
    return MessageReadStateRepository(session)
