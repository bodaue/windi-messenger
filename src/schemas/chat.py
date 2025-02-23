from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.models.chat import ChatType
from src.schemas.user import UserInfo


class ChatCreate(BaseModel):
    user_id: UUID


class ChatMemberInfo(BaseModel):
    user: UserInfo

    model_config = ConfigDict(from_attributes=True)


class ChatInfo(BaseModel):
    id: UUID
    name: str
    type: ChatType
    members: list[ChatMemberInfo]
    group_id: UUID | None

    model_config = ConfigDict(from_attributes=True)
