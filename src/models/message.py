from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.models.user import User
    from src.models.chat import Chat


class Message(Base):
    __table__ = "messages"

    text: Mapped[str] = mapped_column(String(4096))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"))
    chat: Mapped["Chat"] = relationship(back_populates="messages")

    sender_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    sender: Mapped["User"] = relationship(back_populates="messages")
