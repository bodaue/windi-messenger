from datetime import datetime
from uuid import UUID

from sqlalchemy import String, ForeignKey, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, IdMixin, TimestampMixin
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.models.user import User
    from src.models.chat import Chat


class Message(IdMixin, TimestampMixin, Base):
    __tablename__ = "messages"

    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chats.id"))
    chat: Mapped["Chat"] = relationship(back_populates="messages")

    sender_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    sender: Mapped["User"] = relationship()

    text: Mapped[str] = mapped_column(String(4096))

    read_states: Mapped[list["MessageReadState"]] = relationship(
        back_populates="message"
    )


class MessageReadState(IdMixin, Base):
    __tablename__ = "message_read_states"

    message_id: Mapped[UUID] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE")
    )
    message: Mapped["Message"] = relationship(back_populates="read_states")

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship()

    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("message_id", "user_id", name="uq_message_read_state"),
    )
