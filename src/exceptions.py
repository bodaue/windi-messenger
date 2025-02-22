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


class UserNotFoundException(ApplicationException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "User not found"


class ChatAlreadyExistsException(ApplicationException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Chat already exists"


class ChatNotFoundException(ApplicationException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Chat not found"


class GroupNotFoundException(ApplicationException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Group not found"


class InvalidChatParticipantException(ApplicationException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Invalid chat participant"


class MessageNotFoundException(ApplicationException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Message not found"


class AccessDenied(ApplicationException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Access denied"
