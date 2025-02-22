from enum import Enum
from uuid import UUID

from sqlalchemy import String, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, IdMixin, TimestampMixin, CreatedDateMixin
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.models.user import User
    from src.models.group import Group
    from src.models.message import Message


class ChatType(Enum):
    PERSONAL = "personal"
    GROUP = "group"


class Chat(IdMixin, TimestampMixin, Base):
    __tablename__ = "chats"

    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[ChatType]

    group_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("groups.id", ondelete="CASCADE")
    )
    group: Mapped["Group"] = relationship(back_populates="chat")

    messages: Mapped[list["Message"]] = relationship(back_populates="chat")
    members: Mapped[list["ChatMember"]] = relationship(back_populates="chat")

    __table_args__ = (
        CheckConstraint(
            "(type = 'personal' AND group_id IS NULL) OR "
            "(type = 'group' AND group_id IS NOT NULL)",
            name="check_chat_type",
        ),
    )


class ChatMember(IdMixin, CreatedDateMixin, Base):
    __tablename__ = "chat_members"

    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    chat: Mapped["Chat"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship()

    __table_args__ = (
        UniqueConstraint("chat_id", "user_id", name="chat_members_unique"),
    )
