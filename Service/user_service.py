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
    user = user_repository.find_user_by_user_id(session=session, user_id=user_id)
    if user is None:
        raise UserValidationError("User not found")
    user_repository.delete_user_by_id(session=session, user_id=user_id)