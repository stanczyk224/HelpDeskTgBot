from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
from db import Base
from Enums.notification_kind_enum import NotificationKind


class TicketNotification(Base):
    __tablename__ = 'ticket_notifications'

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), nullable=False)
    chat_id: Mapped[int] = mapped_column(nullable=False)
    message_id: Mapped[int] = mapped_column(nullable=False)
    kind: Mapped[NotificationKind] = mapped_column(Enum(NotificationKind), nullable=False)

    def __repr__(self) -> str:
        return f"<TicketNotification ticket_id={self.ticket_id} chat_id={self.chat_id} kind={self.kind}>"