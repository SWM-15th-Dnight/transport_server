from enum import Enum as PEnum

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, Float, Enum
from sqlalchemy.orm import relationship

from config import Base

class Status(PEnum):
    TENTATIVE = "TENTATIVE"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class Transp(PEnum):
    OPAQUE = "OPAQUE"
    TRANSPARENT = "TRANSPARENT"
    
class InputType(Base):
    __tablename__ = "input_type"
    
    input_type_id = Column(Integer, primary_key=True, autoincrement=True)
    input_type = Column(String, nullable=False)
    

class EventMain(Base):
    __tablename__ = "event_main"
    
    event_id = Column(Integer, primary_key=True, autoincrement=True)
    summary = Column(String(50), nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    priority = Column(Integer, nullable=False, default=5)
    repeat_rule = Column(String(255), nullable=True)
    is_deleted = Column(Integer, nullable=False)
    
    calendar_id = Column(Integer, ForeignKey("calendars.calendar_id"), nullable=False)
    
    calendar = relationship("Calendars", lazy = "select")
    
    event_detail = relationship("EventDetail", back_populates="event_main", uselist=False, lazy= "select")


class EventDetail(Base):
    """
    event group, ai processing event 등은 구현하지 않음.
    """
    __tablename__ = "event_detail"
    
    event_detail_id = Column(Integer, ForeignKey('event_main.event_id'), primary_key=True)
    event_main = relationship("EventMain", back_populates="event_detail", lazy="select")
    
    uid = Column(String(255), unique=True)
    sequence = Column(Integer, default=0)
    description = Column(String(2047), nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    location = Column(String(255), nullable=True)
    status = Column(Enum(Status), default=Status.CONFIRMED)
    transp = Column(Enum(Transp), default=Transp.OPAQUE)
    input_time_taken = Column(Float, nullable=False)
    
    alarm_id = Column(Integer, ForeignKey('alarm.alarm_id'), nullable=True)
    input_type_id = Column(Integer, ForeignKey("input_type.input_type_id"), nullable=True)
    
    alarm = relationship("Alarm", lazy="select")