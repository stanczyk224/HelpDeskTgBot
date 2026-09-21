from sqlalchemy import select, delete

from Models.ticket_model import Ticket
from Enums.status_enum import Status


def create_ticket(session, ticket: Ticket):
    session.add(ticket)
    session.commit()


def find_ticket_by_id(session, ticket_id: int):
    stmt = select(Ticket).where(Ticket.id == ticket_id)
    return session.execute(stmt).scalar_one_or_none()


def find_tickets_by_user_id(session, user_id: int):
    stmt = select(Ticket).where(Ticket.user_id == user_id)
    return session.execute(stmt).scalars().all()


def find_tickets_by_status(session, status: Status):
    stmt = select(Ticket).where(Ticket.status == status)
    return session.execute(stmt).scalars().all()


def edit_title(session, ticket_id: int, title: str):
    ticket = find_ticket_by_id(session, ticket_id)
    ticket.title = title
    session.commit()


def edit_description(session, ticket_id: int, description: str):
    ticket = find_ticket_by_id(session, ticket_id)
    ticket.description = description
    session.commit()


def edit_status(session, ticket_id: int, status: Status):
    ticket = find_ticket_by_id(session, ticket_id)
    ticket.status = status
    session.commit()


def delete_ticket_by_id(session, ticket_id: int):
    stmt = delete(Ticket).where(Ticket.id == ticket_id)
    session.execute(stmt)