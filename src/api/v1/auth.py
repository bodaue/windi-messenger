from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from starlette import status

from src.core.di.services import get_auth_service
from src.schemas.user import UserRegister, UserLogin, UserInfo, Token
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


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
