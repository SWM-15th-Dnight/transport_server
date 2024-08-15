from enum import Enum as PEnum

from sqlalchemy import String, Integer, Column, Enum, DateTime, func

from config import Base

class Action(PEnum):
    AUDIO = "AUDIO"
    DISPLAY = "DISPLAY"
    EMAIL = "EMAIL"


class Alarm(Base):
    __tablename__ = "alarm"
    
    alarm_id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(Enum(Action), default=Action.DISPLAY)
    description = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())