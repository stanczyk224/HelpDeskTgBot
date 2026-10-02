import logging

from aiogram.types import Message

from Enums.status_enum import Status
from Models.ticket_model import Ticket
from Models.user_model import User
from Enums.role_enum import Role
from Exceptions.AccessDeniedError import AccessDeniedError
#
# def ensure_can_close_ticket(actor: User) -> None:
#     if actor.role != Role.admin:
#         raise AccessDeniedError("Only admins can close tickets")
#
# def ensure_can_change_role(actor: User, target_id: int) -> None:
#     if actor.role != Role.admin:
#         raise AccessDeniedError("Only admin can change roles")
#     if actor.id == target_id:
#         raise AccessDeniedError("Admins cannot change their own role")
#
# def ensure_can_delete_user(actor: User) -> None:
#     if actor.role != Role.admin:
#         raise AccessDeniedError("Only admin can delete users")

logger = logging.getLogger(__name__)

def ensure_is_admin(actor: User) -> None:
    if actor.role != Role.admin:
        logger.warning(f"{actor} tried to perform admin's action")
        raise AccessDeniedError("Only admin can perform this action!")
def ensure_can_edit_ticket(actor: User, ticket: Ticket) -> None:
    if actor.role == Role.admin:
        logger.info(f"f{actor} edited {ticket}")
        return
    if ticket.user_id != actor.id:
        logger.warning(f"{actor} tried to edit other's tickets")
        raise AccessDeniedError("You can only edit your own tickets")
    if ticket.status != Status.open:
        logger.warning(f"{actor} tried to edit the ticket that is not open")
        raise AccessDeniedError("You can only edit tickets that are still open")
def ensure_is_ticket_author(actor: User, ticket: Ticket) -> None:
    if ticket.user_id != actor.id:
        logger.warning(f"{actor} tried to cancel {ticket.author}'s ticket {ticket}")
        raise AccessDeniedError("You can only cancel your own tickets")
def ensure_can_view_ticket(actor: User, ticket: Ticket) -> None:
    if actor.role == Role.admin:
        logger.info(f"{actor} opened {ticket}")
        return
    if ticket.user_id != actor.id:
        logger.warning(f"{actor} tried to see {ticket}")
        raise AccessDeniedError("You can only see your own tickets")

