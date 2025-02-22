from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from src.schemas.user import UserInfo


class GroupCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    member_ids: list[UUID] | None = None


class GroupMemberInfo(BaseModel):
    user: UserInfo
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GroupInfo(BaseModel):
    id: UUID
    title: str
    creator: UserInfo
    members: list[GroupMemberInfo]

    model_config = ConfigDict(from_attributes=True)


class GroupMemberAdd(BaseModel):
    user_ids: list[UUID]


class GroupMemberRemove(BaseModel):
    user_ids: list[UUID]
