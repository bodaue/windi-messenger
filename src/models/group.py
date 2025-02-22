from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, DateTime, func, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import IdMixin, TimestampMixin, Base
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.models.chat import Chat
    from src.models.user import User


class Group(IdMixin, TimestampMixin, Base):
    __tablename__ = "groups"

    title: Mapped[str]

    creator_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    creator: Mapped["User"] = relationship(back_populates="created_groups")

    chat: Mapped["Chat"] = relationship(back_populates="group")

    members: Mapped[list["GroupMember"]] = relationship(back_populates="group")


class GroupMember(IdMixin, Base):
    __tablename__ = "group_members"

    group_id: Mapped[UUID] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    group: Mapped["Group"] = relationship(
        back_populates="members", cascade="all, delete"
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship()

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uq_group_member"),
        Index("idx_group_members_group", "group_id"),
        Index("idx_group_members_user", "user_id"),
    )
