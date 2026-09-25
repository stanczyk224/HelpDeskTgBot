from datetime import datetime
from sqlalchemy import ForeignKey, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Models.user_model import User
from db import Base
from Enums.status_enum import Status


class Ticket(Base):
    __tablename__ = 'tickets'

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(nullable=False)

    description: Mapped[str] = mapped_column(nullable=False)

    photo_id: Mapped[str] = mapped_column(nullable=True)

    status: Mapped[Status] = mapped_column(
        Enum(Status),
        nullable=False)

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False)

    assigned_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True)

    completed_by_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True)

    author: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="tickets"
    )

    assigned_admin: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[assigned_admin_id])
    completed_by_admin: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[completed_by_admin_id]
    )

    def __repr__(self) -> str:
        return f"<Ticket id={self.id} title={self.title!r} status={self.status} user_id={self.user_id}>"