from enum import Enum as PEnum

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func, Float, Enum
from sqlalchemy.orm import relationship, mapped_column

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
    
    input_type_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    input_type = mapped_column(String, nullable=False)
    

class EventMain(Base):
    __tablename__ = "event_main"
    
    event_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    summary = mapped_column(String(50), nullable=False)
    start_at = mapped_column(DateTime, nullable=False)
    end_at = mapped_column(DateTime, nullable=False)
    priority = mapped_column(Integer, nullable=False, default=5)
    repeat_rule = mapped_column(String(255), nullable=True)
    is_deleted = mapped_column(Integer, nullable=False)
    
    calendar_id = mapped_column(Integer, ForeignKey("calendars.calendar_id"), nullable=False)
    
    calendar = relationship("Calendars", lazy = "select")
    
    event_detail = relationship("EventDetail", back_populates="event_main", uselist=False, lazy= "select")


class EventDetail(Base):
    """
    event group, ai processing event 등은 구현하지 않음.
    """
    __tablename__ = "event_detail"
    
    event_detail_id = mapped_column(Integer, ForeignKey('event_main.event_id'), primary_key=True)
    event_main = relationship("EventMain", back_populates="event_detail", lazy="select")
    
    uid = mapped_column(String(255), unique=True)
    sequence = mapped_column(Integer, default=0)
    description = mapped_column(String(2047), nullable=True)
    created_at = mapped_column(DateTime, default=func.current_timestamp())
    updated_at = mapped_column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    location = mapped_column(String(255), nullable=True)
    status = mapped_column(Enum(Status), default=Status.CONFIRMED)
    transp = mapped_column(Enum(Transp), default=Transp.OPAQUE)
    input_time_taken = mapped_column(Float, nullable=False)
    
    alarm_id = mapped_column(Integer, ForeignKey('alarm.alarm_id'), nullable=True)
    input_type_id = mapped_column(Integer, ForeignKey("input_type.input_type_id"), nullable=True)
    
    alarm = relationship("Alarm", lazy="select")