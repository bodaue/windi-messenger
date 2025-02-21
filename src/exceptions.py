from fastapi import HTTPException
from starlette import status


class ApplicationException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = ""

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(
            status_code=self.status_code, detail=detail if detail else self.detail
        )


class InvalidTokenException(ApplicationException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid token"


class InvalidCredentialsException(ApplicationException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Invalid token"


class UserAlreadyExistsException(ApplicationException):
    status_code = status.HTTP_409_CONFLICT
    detail = "User already exists"
