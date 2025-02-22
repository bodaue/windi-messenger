from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import config
from src.core.di.database import get_session
from src.repositories.user import UserRepository
from src.services.auth import AuthService
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
