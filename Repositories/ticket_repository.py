from sqlalchemy import select, delete

from Models.ticket_model import Ticket
from Enums.status_enum import Status


def create_ticket(session, ticket: Ticket):
    session.add(ticket)
    session.commit()

def find_all_tickets(session):
    stmt = select(Ticket)
    return session.execute(stmt).scalars().all()

def find_ticket_by_id(session, ticket_id: int):
    stmt = select(Ticket).where(Ticket.id == ticket_id)
    return session.execute(stmt).scalar_one_or_none()


def find_tickets_by_user_id(session, user_id: int):
    stmt = select(Ticket).where(Ticket.user_id == user_id)
    return session.execute(stmt).scalars().all()


def find_tickets_by_status(session, status: Status):
    stmt = select(Ticket).where(Ticket.status == status)
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

def delete_ticket_by_id(session, ticket_id: int) -> bool:
    ticket = find_ticket_by_id(session, ticket_id)
    if ticket is None:
        return False
    stmt = delete(Ticket).where(Ticket.id == ticket_id)
    session.execute(stmt)
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