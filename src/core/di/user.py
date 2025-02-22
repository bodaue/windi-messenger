from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.di.repositories import get_user_repository
from src.core.di.services import get_token_service
from src.exceptions import InvalidTokenException
from src.models.user import User
from src.repositories.user import UserRepository
from src.services.token import TokenService

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> User:
    user_id = token_service.decode_token(credentials.credentials)

    user = await user_repository.get_by_id(user_id)
    if not user:
        raise InvalidTokenException

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
