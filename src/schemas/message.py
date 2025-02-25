from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from src.schemas.user import UserInfo


class MessageCreate(BaseModel):
    chat_id: UUID
    text: str = Field(min_length=1, max_length=4096)
    idempotency_key: str = Field(min_length=1, max_length=64)


class MessageRead(BaseModel):
    chat_id: UUID
    message_id: UUID


class MessageInfo(BaseModel):
    id: UUID
    chat_id: UUID
    sender: UserInfo
    text: str
    created_at: datetime
    is_read: bool = False
    read_at: datetime | None = None
    idempotency_key: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ChatHistoryRequest(BaseModel):
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
