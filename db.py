from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

engine = create_engine('sqlite:///helpdesk.db',echo=True)
Session = sessionmaker(bind=engine)
session = Session()

class Base(DeclarativeBase):
    pass






