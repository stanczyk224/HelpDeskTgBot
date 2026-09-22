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

def ensure_is_admin(actor: User) -> None:
    if actor.role != Role.admin:
        raise AccessDeniedError("Only admin can perform this action!")
def ensure_can_edit_ticket(actor: User, ticket: Ticket) -> None:
    if actor.role == Role.admin:
        return
    if ticket.user_id != actor.id:
        raise AccessDeniedError("You can only edit your own tickets")
    if ticket.status != Status.open:
        raise AccessDeniedError("You can only edit tickets that are still open")