from enum import Enum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, IdMixin, TimestampMixin


class ChatType(Enum):
    PERSONAL = "personal"
    GROUP = "group"


class Chat(IdMixin, TimestampMixin, Base):
    __table__ = "chats"

    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[ChatType]
