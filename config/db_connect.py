from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .env import DB_HOST, DB_PASSWORD, DB_PORT, DB_USER, DB_TABLE

_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_TABLE}"

_engine = create_engine(url=_url, echo=True)

_Session = sessionmaker(bind=_engine, autocommit=False, autoflush=True)

class Base(DeclarativeBase):
    pass

def get_db():
    db = _Session()
    try:
        yield db
    finally:
        db.close()