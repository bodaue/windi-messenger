from datetime import datetime
from uuid import UUID

from sqlalchemy import String, ForeignKey, DateTime, UniqueConstraint, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, IdMixin, TimestampMixin
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.models.user import User
    from src.models.chat import Chat


class Message(IdMixin, TimestampMixin, Base):
    __tablename__ = "messages"

    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chats.id", ondelete="CASCADE"))
    chat: Mapped["Chat"] = relationship(back_populates="messages")

    sender_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    sender: Mapped["User"] = relationship()

    text: Mapped[str] = mapped_column(String(4096))

    idempotency_key: Mapped[str | None] = mapped_column(String(64))

    read_states: Mapped[list["MessageReadState"]] = relationship(
        back_populates="message"
    )

    __table_args__ = (
        Index("ix_messages_chat_created", "chat_id", "created_at"),
        UniqueConstraint(
            "sender_id", "idempotency_key", name="uq_sender_idempotency_key"
        ),
    )


class MessageReadState(IdMixin, Base):
    __tablename__ = "message_read_states"

    message_id: Mapped[UUID] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE")
    )
    message: Mapped["Message"] = relationship(back_populates="read_states")

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship()

    read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("message_id", "user_id", name="uq_message_read_state"),
    )
