from enum import Enum as PEnum

from sqlalchemy import String, Integer, Enum, DateTime, func
from sqlalchemy.orm import mapped_column

from config import Base

class Action(PEnum):
    AUDIO = "AUDIO"
    DISPLAY = "DISPLAY"
    EMAIL = "EMAIL"


class Alarm(Base):
    __tablename__ = "alarm"
    
    alarm_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    action = mapped_column(Enum(Action), default=Action.DISPLAY)
    alarm_trigger = mapped_column(String(255), nullable=False)
    description = mapped_column(String(50), nullable=True)
    created_at = mapped_column(DateTime, default=func.current_timestamp())
    updated_at = mapped_column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())