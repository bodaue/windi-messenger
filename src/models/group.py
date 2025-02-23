from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import IdMixin, TimestampMixin, Base
from typing import TYPE_CHECKING
from src.models.chat import ChatMember


if TYPE_CHECKING:
    from src.models.chat import Chat
    from src.models.user import User


class Group(IdMixin, TimestampMixin, Base):
    __tablename__ = "groups"

    title: Mapped[str]

    creator_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    creator: Mapped["User"] = relationship(back_populates="created_groups")

    chat: Mapped["Chat"] = relationship(back_populates="group")

    @hybrid_property
    def members(self) -> list[ChatMember]:
        return self.chat.members
