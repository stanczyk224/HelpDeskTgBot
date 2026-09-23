from sqlalchemy import select, delete
from Models.ticket_notification_model import TicketNotification
from Enums.notification_kind_enum import NotificationKind


def create_notification(session, ticket_id: int, chat_id: int, message_id: int, kind: NotificationKind) -> TicketNotification:
    notification = TicketNotification(
        ticket_id=ticket_id,
        chat_id=chat_id,
        message_id=message_id,
        kind=kind
    )
    session.add(notification)
    session.commit()
    return notification


def find_by_ticket_id(session, ticket_id: int):
    stmt = select(TicketNotification).where(TicketNotification.ticket_id == ticket_id)
    return session.execute(stmt).scalars().all()


def delete_by_ticket_id(session, ticket_id: int):
    stmt = delete(TicketNotification).where(TicketNotification.ticket_id == ticket_id)
    session.execute(stmt)
    session.commit()