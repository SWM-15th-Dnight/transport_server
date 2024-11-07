from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, mapped_column

from config import Base

class ExportCalendar(Base):
    __tablename__ = "export_calendar"
    
    export_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_count = mapped_column(Integer, default=0, nullable=False)
    export_uid = mapped_column(String)
    created_at = mapped_column(DateTime, default=func.now())
    
    calendar_id = mapped_column(Integer, ForeignKey("calendars.calendar_id"))
    calendar = relationship("Calendars")