from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

engine = create_engine('sqlite:///helpdesk.db',echo=True)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass






