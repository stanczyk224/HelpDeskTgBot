from Exceptions.TicketValidationError import TicketValidationError
from Models.ticket_model import Ticket
from Enums.status_enum import Status
from Models.user_model import User
from Repositories import ticket_repository
from Utils import validators
from Service.access_control import ensure_is_admin, ensure_can_edit_ticket


def create_ticket(session, description: str, user_id: int, title: str, photo_id: str | None = None):
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
    ticket_repository.create_ticket(session, ticket)

def close_ticket(session, actor: User, ticket_id: int):
    ensure_is_admin(actor)
    ticket = ticket_repository.find_ticket_by_id(session=session, ticket_id=ticket_id)
    if ticket is None:
        raise TicketValidationError("Ticket not found")
    if ticket.status == Status.closed:
        raise TicketValidationError("Ticket is already closed")
    ticket_repository.edit_status(session=session, ticket_id=ticket_id, status=Status.closed)

def take_ticket_in_progress(session, actor: User, ticket_id: int):
    ensure_is_admin(actor)
    ticket = ticket_repository.find_ticket_by_id(session=session,  ticket_id=ticket_id)
    if ticket is None:
        raise TicketValidationError("Ticket not found")
    if ticket.status == Status.closed:
        raise TicketValidationError("Cannot take a closed ticket into progress")
    ticket_repository.assign_and_set_status(session=session,  ticket_id=ticket_id, actor_id=actor.id, status=Status.in_progress)

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