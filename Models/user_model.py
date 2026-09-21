from sqlalchemy import Enum

from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Models.ticket_model import Ticket

from db import Base
from Enums.role_enum import Role

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(nullable=False)
    job_title: Mapped[str] = mapped_column(nullable=False)
    cabinet: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role),nullable=False)
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="user")


