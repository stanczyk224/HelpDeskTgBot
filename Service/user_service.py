from Enums.status_enum import Status
from Exceptions.UserValidationError import UserValidationError
from Enums.role_enum import Role
from Models.user_model import User
from Repositories import user_repository
from Utils import validators
from Service.access_control import ensure_is_admin


def register_user(session,telegram_id: int, full_name: str, job_title: str, cabinet: str, role: Role):
    if not validators.is_not_empty(full_name):
        raise UserValidationError("Full name cannot be empty")
    if not validators.has_no_digits(full_name):
        raise UserValidationError("No digits in the name allowed")
    if not validators.is_long_enough(full_name, 3):
        raise UserValidationError("The name is too short")

    if not validators.is_not_empty(job_title):
        raise UserValidationError("Job title cannot be empty")
    if not validators.has_no_digits(job_title):
        raise UserValidationError("No digits in the job title allowed")

    if not validators.is_not_empty(cabinet):
        raise UserValidationError("Cabinet cannot be empty")

    user = User(
        telegram_id=telegram_id,
        full_name=full_name,
        job_title=job_title,
        cabinet=cabinet,
        role=role
    )
    return user_repository.create_user(session=session, user=user)

def get_users_page(
    session,
    actor: User,
    page: int,
    per_page: int = 10,
):
    ensure_is_admin(actor)

    users = user_repository.find_users_page(
        session=session,
        page=page,
        per_page=per_page,
    )

    total_users = user_repository.count_users(
        session=session,
    )

    return users, total_users

def get_user_by_telegram_id(session, telegram_id: int):
    return user_repository.find_user_by_telegram_id(
        session=session,
        telegram_id=telegram_id,
    )
def get_user_by_id(session, user_id: int):
    return user_repository.find_user_by_user_id(
        session=session,
        user_id=user_id,
    )

def promote_to_admin(session,actor: User, user_id: int):
    ensure_is_admin(actor)
    user = user_repository.find_user_by_user_id(session=session, user_id=user_id)
    if user is None:
        raise UserValidationError("User not found")
    user_repository.edit_role(session=session, role=Role.admin, user_id=user_id)


def demote_to_user(session, actor: User, user_id: int):
    ensure_is_admin(actor)
    user = user_repository.find_user_by_user_id(session=session, user_id=user_id)
    if user is None:
        raise UserValidationError("User not found")
    user_repository.edit_role(session=session, role=Role.user, user_id=user_id)


def remove_user(session, actor: User, user_id: int):
    ensure_is_admin(actor)

    user = user_repository.find_user_by_user_id(
        session=session,
        user_id=user_id,
    )

    if user is None:
        raise UserValidationError("User not found")

    # Проверяем открытые тикеты
    open_tickets = [
        ticket
        for ticket in user.tickets
        if ticket.status == Status.open
    ]

    if open_tickets:
        raise UserValidationError(
            "Сначала закройте все открытые тикеты пользователя"
        )

    # Все тикеты пользователя уже закрыты.
    # Удаляем их, затем самого пользователя.
    user_repository.delete_user_with_tickets(
        session=session,
        user=user,
    )
