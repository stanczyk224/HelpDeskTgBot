from sqlalchemy import select
from sqlalchemy.orm import Session
from Enums.role_enum import Role
from Models.user_model import User

# CREATE
def create_user(session:Session,user: User):
    session.add(user)
    session.commit()

# DELETE
def delete_user_by_id(session,user_id: int) -> bool:
    user = find_user_by_user_id(session=session,user_id=user_id)
    if user is None:
        return False
    session.delete(user)
    session.commit()
    return True

# FIND
def find_all_users(session):
    stmt = select(User)
    return session.execute(stmt).scalars().all()

def find_user_by_user_id(session,user_id):
    stmt = select(User).where(User.id == user_id)
    return session.execute(stmt).scalar_one_or_none()

def find_user_by_full_name(session,full_name):
    stmt = select(User).where(User.full_name == full_name)
    return session.execute(stmt).scalar_one_or_none()

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