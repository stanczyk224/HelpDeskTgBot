from sqlalchemy.orm import Session

from Enums.role_enum import Role
from Exceptions.TicketValidationError import TicketValidationError
from Models.ticket_model import Ticket
from Enums.status_enum import Status
from Models.user_model import User
from Repositories import ticket_repository
from Utils import validators
from Service.access_control import ensure_is_admin, ensure_can_edit_ticket, ensure_is_ticket_author


def create_ticket(session, description: str, user_id: int, title: str, photo_id: str | None = None) -> Ticket:
    if not validators.is_not_empty(description):
        raise TicketValidationError("Description cannot be empty")
    if not validators.is_long_enough(description, 5):
        raise TicketValidationError("Description is too short")

    ticket = Ticket(
        title=title,
        description=description,
        photo_id=photo_id,
        status=Status.open,
        user_id=user_id
    )
    return ticket_repository.create_ticket(session, ticket)
def get_ticket_by_id(
        session: Session,
        ticket_id: int
):
    return ticket_repository.find_ticket_by_id(
        session=session,
        ticket_id=ticket_id)
def get_tickets_by_status_and_user(
        session: Session,
        actor: User,
        status: Status,
        user_id: int
):
    ensure_is_admin(actor)
    return ticket_repository.find_tickets_by_status_and_user(
        session=session,
        status=status,
        user_id=user_id
    )

def get_ticket_by_user_id(
        session,
        user_id: int
):
    return ticket_repository.find_tickets_by_user_id(
        session=session,
        user_id=user_id)

def get_tickets_page(
        session,
        actor: User,
        page: int,
        per_page: int = 10
):
    if actor.role == Role.admin:
        tickets = ticket_repository.find_tickets_page(
            session=session,
            page=page,
            per_page=per_page
        )
        total_tickets = ticket_repository.count_tickets(
            session=session
        )
        return tickets, total_tickets
    else:
        tickets = ticket_repository.find_user_tickets_page(
            session=session,
            user_id=actor.id,
            page=page,
            per_page=per_page
        )
        total_tickets = ticket_repository.count_tickets_by_user_id(
            session=session,
            user_id=actor.id,
        )
        return tickets, total_tickets
def close_ticket(session, actor: User, ticket_id: int) -> Ticket:
    ensure_is_admin(actor)

    ticket = ticket_repository.find_ticket_by_id(
        session=session,
        ticket_id=ticket_id
    )

    if ticket is None:
        raise TicketValidationError("Ticket not found")

    if ticket.status == Status.closed:
        raise TicketValidationError("Ticket is already closed")

    ticket_repository.close_with_timestamp(
        session=session,
        ticket_id=ticket_id,
        completed_by_admin_id=actor.id
    )

    return ticket

def cancel_ticket(session, actor: User, ticket_id: int) -> Ticket:

    ticket = ticket_repository.find_ticket_by_id(session=session, ticket_id=ticket_id)

    if ticket is None:
        raise TicketValidationError("Ticket not found")

    ensure_is_ticket_author(actor, ticket)

    if ticket.status != Status.open:
        raise TicketValidationError("Only open tickets can be cancelled")

    ticket_repository.close_with_timestamp(
        session=session,
        ticket_id=ticket_id,
        completed_by_admin_id=actor.id
    )

    return ticket

def complete_ticket(
        session: Session,
        actor: User,
        ticket_id: int,
):
    ensure_is_admin(actor)

    ticket = ticket_repository.find_ticket_by_id(
        session=session,
        ticket_id=ticket_id
    )

    if ticket is None:
        raise TicketValidationError("Ticket not found")
    print(
        "COMPLETE:",
        ticket.id,
        ticket.status,
        ticket.assigned_admin_id
    )
    if ticket.status != Status.in_progress:
        raise TicketValidationError(
            "Only tickets in progress can be completed"
        )

    ticket_repository.close_with_timestamp(
        session=session,
        ticket_id=ticket_id,
        completed_by_admin_id=actor.id
    )

    return ticket

def take_ticket_in_progress(session, actor: User, ticket_id: int) -> Ticket:
    ensure_is_admin(actor)
    ticket = ticket_repository.find_ticket_by_id(session=session, ticket_id=ticket_id)
    if ticket is None:
        raise TicketValidationError("Ticket not found")
    print(
        "TAKE BEFORE:",
        ticket.id,
        ticket.status
    )
    if ticket.status == Status.closed or ticket.status == Status.in_progress:
        raise TicketValidationError("Cannot take a closed ticket into progress")
    ticket_repository.assign_and_set_status(session=session, ticket_id=ticket_id, actor_id=actor.id, status=Status.in_progress)
    print(
        "TAKE AFTER:",
        ticket.id,
        ticket.status,
        ticket.assigned_admin_id
    )
    return ticket


def update_ticket_title(session, actor: User, ticket_id: int, new_title: str):
    ticket = ticket_repository.find_ticket_by_id(session=session, ticket_id=ticket_id)
    if ticket is None:
        raise TicketValidationError("Ticket not found")
    ensure_can_edit_ticket(actor, ticket)
    if not validators.is_not_empty(new_title):
        raise TicketValidationError("Title cannot be empty")
    ticket_repository.edit_title(session=session, ticket_id=ticket_id, title=new_title)


def update_ticket_description(session, actor: User, ticket_id: int, new_description: str):
    ticket = ticket_repository.find_ticket_by_id(session=session, ticket_id=ticket_id)
    if ticket is None:
        raise TicketValidationError("Ticket not found")
    ensure_can_edit_ticket(actor, ticket)
    if not validators.is_not_empty(new_description):
        raise TicketValidationError("Description cannot be empty")
    if not validators.is_long_enough(new_description, 5):
        raise TicketValidationError("Description is too short")
    ticket_repository.edit_description(session=session, ticket_id=ticket_id, description=new_description)


def reopen_ticket(session, actor: User, ticket_id: int):
    ensure_is_admin(actor)
    ticket = ticket_repository.find_ticket_by_id(session=session, ticket_id=ticket_id)
    if ticket is None:
        raise TicketValidationError("Ticket not found")
    if ticket.status != Status.closed:
        raise TicketValidationError("Only closed tickets can be reopened")
    ticket_repository.edit_status(session=session, ticket_id=ticket_id, status=Status.open)

def delete_ticket_by_id(
        session: Session,
        actor: User,
        ticket_id: int
):
    ensure_is_admin(actor)
    ticket = ticket_repository.find_ticket_by_id(session=session, ticket_id=ticket_id)
    if ticket is None:
        raise TicketValidationError("Ticket not found")
    ticket_repository.delete_ticket_by_id(
        session=session,
        ticket_id=ticket_id
    )
