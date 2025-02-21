from datetime import timedelta, datetime, UTC  # noqa: A005
from uuid import UUID

from jose import jwt, JWTError

from src.core.config import JWTConfig
from src.exceptions import InvalidTokenException


class TokenService:
    def __init__(self, config: JWTConfig) -> None:
        self._config = config

    def create_access_token(
        self,
        user_id: UUID,
        expires_delta: timedelta | None = None,
    ) -> str:
        to_encode = {"sub": str(user_id)}

        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                minutes=self._config.access_token_expires_minutes,
            )

        to_encode.update({"exp": expire})

        return jwt.encode(
            to_encode,
            self._config.secret_key.get_secret_value(),
            algorithm=self._config.algorithm,
        )

    def decode_token(self, token: str) -> UUID:
        try:
            payload = jwt.decode(
                token,
                self._config.secret_key.get_secret_value(),
                algorithms=[self._config.algorithm],
            )
            user_id: str | None = payload.get("sub")
            if user_id is None:
                raise InvalidTokenException
            return UUID(user_id)
        except JWTError as e:
            raise InvalidTokenException from e
