from sqlalchemy import String, Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from config import Base

class ExportCalendar(Base):
    __tablename__ = "export_calendar"
    
    export_id = Column(Integer, primary_key=True, autoincrement=True)
    event_count = Column(Integer, default=0, nullable=False)
    export_uid = Column(String)
    created_at = Column(DateTime, default=func.now())
    
    calendar_id = Column(Integer, ForeignKey("calendars.calendar_id"))
    calendar = relationship("Calendars")