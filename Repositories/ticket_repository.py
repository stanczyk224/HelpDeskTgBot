from datetime import datetime, UTC
from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session

from Models.ticket_model import Ticket
from Enums.status_enum import Status
from Models.user_model import User
from Repositories import ticket_notification_repository


def create_ticket(session, ticket: Ticket) -> Ticket:
    session.add(ticket)
    session.commit()
    return ticket


def find_ticket_by_id(session, ticket_id: int):
    stmt = select(Ticket).where(Ticket.id == ticket_id)
    return session.execute(stmt).scalar_one_or_none()

def find_tickets_by_user_id(session, user_id: int):
    stmt = select(Ticket).where(Ticket.user_id == user_id)
    return session.execute(stmt).scalars().all()


def find_tickets_by_status(session, status: Status):
    stmt = select(Ticket).where(Ticket.status == status)
    return session.execute(stmt).scalars().all()
def find_tickets_by_status_and_user(session: Session, status: Status, user_id: int):
    stmt = select(Ticket).where(
        Ticket.status == status,
        Ticket.user_id == user_id)
    return session.execute(stmt).scalars().all()


def find_all_tickets(session):
    stmt = select(Ticket)
    return session.execute(stmt).scalars().all()

def find_tickets_page(
        session,
        page: int,
        per_page: int = 10
):
    offset = (page - 1) * per_page

    stmt = (
        select(Ticket)
        .order_by(Ticket.id)
        .offset(offset)
        .limit(per_page)
    )
    return session.execute(stmt).scalars().all()

def find_user_tickets_page(
        session: Session,
        user_id: int,
        page: int,
        per_page: int = 10
):
    offset = (page - 1) * per_page

    stmt = (
        select(Ticket)
        .where(Ticket.user_id == user_id)
        .order_by(Ticket.id)
        .offset(offset)
        .limit(per_page)
    )
    return session.execute(stmt).scalars().all()

def count_tickets(session):
    stmt = select(func.count()).select_from(Ticket)
    return session.execute(stmt).scalar_one()

def count_tickets_by_user_id(session,user_id: int):
    stmt = (
        select(func.count())
        .select_from(Ticket)
        .where(Ticket.user_id == user_id)
    )
    return session.execute(stmt).scalar_one()

def find_closed_before(session, cutoff: datetime):
    stmt = select(Ticket).where(Ticket.status == Status.closed, Ticket.closed_at < cutoff)
    return session.execute(stmt).scalars().all()

def edit_title(session, ticket_id: int, title: str) -> bool:
    ticket = find_ticket_by_id(session, ticket_id)
    if ticket is None:
        return False
    ticket.title = title
    session.commit()
    return True

def edit_description(session, ticket_id: int, description: str) -> bool:
    ticket = find_ticket_by_id(session, ticket_id)
    if ticket is None:
        return False
    ticket.description = description
    session.commit()
    return True

def edit_status(session, ticket_id: int, status: Status) -> bool:
    ticket = find_ticket_by_id(session, ticket_id)
    if ticket is None:
        return False
    ticket.status = status
    session.commit()
    return True

def close_with_timestamp(
        session: Session,
        ticket_id: int,
        completed_by_admin_id: int
) -> bool:
    ticket = find_ticket_by_id(session, ticket_id)

    if ticket is None:
        return False

    ticket.status = Status.closed
    ticket.closed_at = datetime.now(UTC)
    ticket.completed_by_admin_id = completed_by_admin_id
    session.commit()
    return True

def delete_ticket_by_id(session: Session, ticket_id: int) -> bool:
    ticket = find_ticket_by_id(session=session,ticket_id=ticket_id)
    if ticket is None:
        return False

    ticket_notification_repository.delete_by_ticket_id(
        session=session,
        ticket_id=ticket_id)

    session.delete(ticket)
    session.commit()
    return True

def assign_and_set_status(session, ticket_id, actor_id: int, status: Status) -> bool:
    ticket = find_ticket_by_id(session, ticket_id)
    if ticket is None:
        return False
    ticket.status = status
    ticket.assigned_admin_id = actor_id
    session.commit()
    return True