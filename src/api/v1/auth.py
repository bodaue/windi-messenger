from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.config import config
from src.core.di.database import get_session
from src.repositories.user import UserRepository
from src.schemas.user import UserRegister, UserLogin, UserInfo, Token
from src.services.auth import AuthService
from src.services.password_hasher import PasswordService
from src.services.token import TokenService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_token_service() -> TokenService:
    return TokenService(config=config.jwt)


def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> AuthService:
    return AuthService(
        session, UserRepository(session), PasswordService(), token_service
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegister,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserInfo:
    return await service.register_user(data)


@router.post("/login")
async def login(
    data: UserLogin,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    return await service.login_user(data)
