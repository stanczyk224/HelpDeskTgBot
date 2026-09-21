from Exceptions.TicketValidationError import TicketValidationError
from Models.ticket_model import Ticket
from Enums.status_enum import Status
from Repositories import ticket_repository
from Utils import validators


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


def close_ticket(session, ticket_id: int):
    ticket = ticket_repository.find_ticket_by_id(session, ticket_id)
    if ticket is None:
        raise TicketValidationError("Ticket not found")
    ticket_repository.edit_status(session, ticket_id, Status.closed)


def update_ticket_status(session, ticket_id: int, new_status: Status):
    ticket = ticket_repository.find_ticket_by_id(session, ticket_id)
    if ticket is None:
        raise TicketValidationError("Ticket not found")
    ticket_repository.edit_status(session, ticket_id, new_status)