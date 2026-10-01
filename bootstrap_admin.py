from db import SessionLocal
from Repositories import user_repository
from Enums.role_enum import Role
from Models.user_model import User
from Models.ticket_model import Ticket

with SessionLocal() as session:
    success = user_repository.edit_role(session, role=Role.admin, user_id=1)
    print(f"Promoted: {success}")