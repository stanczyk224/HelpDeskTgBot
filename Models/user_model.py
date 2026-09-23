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
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(nullable=False)
    job_title: Mapped[str] = mapped_column(nullable=False)
    cabinet: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False)

    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        foreign_keys="[Ticket.user_id]",
        back_populates="author"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} telegram_id={self.telegram_id} full_name={self.full_name!r} role={self.role}>"