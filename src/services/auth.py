from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import InvalidCredentialsException, UserAlreadyExistsException
from src.models import User
from src.repositories.user import UserRepository
from src.schemas.user import UserInfo, UserRegister, UserLogin, Token

from src.services.password_hasher import PasswordService
from src.services.token import TokenService


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        password_service: PasswordService,
        token_service: TokenService,
    ) -> None:
        self._session = session
        self._user_repository = user_repository
        self._password_service = password_service
        self._token_service = token_service

    async def register_user(self, data: UserRegister) -> UserInfo:
        existing_user = await self._user_repository.get_by_email(data.email)
        if existing_user:
            raise UserAlreadyExistsException

        hashed_password = self._password_service.get_password_hash(data.password)
        user = User(name=data.name, email=data.email, hashed_password=hashed_password)
        await self._user_repository.create(user)
        await self._session.commit()

        return UserInfo.model_validate(user)

    async def login_user(self, data: UserLogin) -> Token:
        user = await self._user_repository.get_by_email(data.email)
        if not user:
            raise InvalidCredentialsException

        if not self._password_service.verify_password(
            data.password, user.hashed_password
        ):
            raise InvalidCredentialsException

        access_token = self._token_service.create_access_token(user.id)

        return Token(access_token=access_token)
