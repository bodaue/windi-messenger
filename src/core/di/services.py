from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import config
from src.core.di.database import get_session
from src.core.di.repositories import (
    get_chat_repository,
    get_chat_member_repository,
    get_user_repository,
)
from src.repositories.chat import ChatRepository
from src.repositories.chat_member import ChatMemberRepository
from src.repositories.user import UserRepository
from src.services.auth import AuthService
from src.services.chat import ChatService
from src.services.password_hasher import PasswordService
from src.services.token import TokenService


def get_token_service() -> TokenService:
    return TokenService(config=config.jwt)


def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> AuthService:
    return AuthService(
        session, UserRepository(session), PasswordService(), token_service
    )


def get_chat_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    chat_repository: Annotated[ChatRepository, Depends(get_chat_repository)],
    chat_member_repository: Annotated[
        ChatMemberRepository, Depends(get_chat_member_repository)
    ],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> ChatService:
    return ChatService(
        session=session,
        chat_repository=chat_repository,
        chat_member_repository=chat_member_repository,
        user_repository=user_repository,
    )
