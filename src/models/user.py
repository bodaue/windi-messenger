from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, IdMixin, TimestampMixin
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.group import Group


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "users"

    name: Mapped[str]
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(200))

    created_groups: Mapped[list["Group"]] = relationship(back_populates="creator")
