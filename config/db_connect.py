from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .env import DB_HOST, DB_PASSWORD, DB_PORT, DB_USERNAME, DB_TABLE_NAME

_url = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_TABLE_NAME}"

_engine = create_engine(url=_url, echo=True, pool_recycle=3600)

_Session = sessionmaker(bind=_engine, autocommit=False, autoflush=True)

class Base(DeclarativeBase):
    pass

def get_db():
    db = _Session()
    try:
        yield db
    finally:
        db.close()