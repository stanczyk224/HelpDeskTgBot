from sqlalchemy import select, func
from sqlalchemy.orm import Session
from Enums.role_enum import Role
from Models.user_model import User

from Models.ticket_notification_model import TicketNotification

# CREATE
def create_user(session:Session,user: User):
    session.add(user)
    session.commit()
    return user

# DELETE
def delete_user_by_id(session,user_id: int) -> bool:
    user = find_user_by_user_id(session=session,user_id=user_id)
    if user is None:
        return False
    session.delete(user)
    session.commit()
    return True

def delete_user_with_tickets(session, user: User):
    for ticket in user.tickets:

        notifications = session.execute(
            select(TicketNotification).where(
                TicketNotification.ticket_id == ticket.id
            )
        ).scalars().all()

        for notification in notifications:
            session.delete(notification)

        session.delete(ticket)

    session.delete(user)
    session.commit()

# FIND
def find_all_users(session):
    stmt = select(User)
    return session.execute(stmt).scalars().all()

def find_users_page(
        session,
        page: int,
        per_page: int = 10
):
    offset = (page - 1) * per_page

    stmt = (
        select(User)
        .order_by(User.id)
        .offset(offset)
        .limit(per_page)
    )
    return session.execute(stmt).scalars().all()

def count_users(session):
    stmt = select(func.count()).select_from(User)
    return session.execute(stmt).scalar_one()

def find_user_by_user_id(session,user_id):
    stmt = select(User).where(User.id == user_id)
    return session.execute(stmt).scalar_one_or_none()

def find_user_by_telegram_id(session, telegram_id: int):
    stmt = select(User).where(User.telegram_id == telegram_id)
    return session.execute(stmt).scalar_one_or_none()

def find_user_by_full_name(session,full_name):
    stmt = select(User).where(User.full_name == full_name)
    return session.execute(stmt).scalar_one_or_none()

def find_users_by_role(session, role: Role):
    stmt = select(User).where(User.role == role)
    return session.execute(stmt).scalars().all()

# EDIT
def edit_full_name(session,new_full_name,user_id:int) -> bool:
    user = find_user_by_user_id(session,user_id)
    if user is None:
        return False
    user.full_name = new_full_name
    session.commit()
    return True

def edit_job_title(session, job_title,user_id:int) -> bool:
    user = find_user_by_user_id(session,user_id)
    if user is None:
        return False
    user.job_title = job_title
    session.commit()
    return True

def edit_cabinet(session, cabinet:"str",user_id:int) -> bool:
    user = find_user_by_user_id(session,user_id)
    if user is None:
        return False
    user.cabinet = cabinet
    session.commit()
    return True

def edit_role(session, role: Role,user_id:int) -> bool:
    user = find_user_by_user_id(session,user_id)
    if user is None:
        return False
    user.role = role
    session.commit()
    return True