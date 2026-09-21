from sqlalchemy import ForeignKey, Enum
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
    status: Mapped[Status] = mapped_column(Enum(Status), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False)
    user: Mapped["User"] = relationship(back_populates="tickets")