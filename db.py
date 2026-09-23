from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


engine = create_engine('sqlite:///helpdesk.db',echo=True)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

from Models.user_model import User
from Models.ticket_model import Ticket
from Models.ticket_notification_model import TicketNotification






