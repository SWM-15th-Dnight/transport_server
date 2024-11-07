from sqlalchemy import String, Integer, ForeignKey, Float, DateTime, func
from sqlalchemy.orm import relationship, mapped_column

from config import Base

class ImportCalendar(Base):
    __tablename__ = "import_calendar"
    
    import_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    is_success = mapped_column(Integer, default=1, nullable=False)
    event_count = mapped_column(Integer, default=1, nullable=False)
    uid = mapped_column(String)
    time_taken = mapped_column(Float)
    fail_count = mapped_column(Integer)
    created_at = mapped_column(DateTime, default=func.now())
    
    calendar_id = mapped_column(Integer, ForeignKey("calendars.calendar_id"))
    
    calendar = relationship("Calendars")
    

class FailedImportEvent(Base):
    __tablename__ = "failed_import_event"
    
    failed_import_event_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    error_log = mapped_column(String(8192), nullable=False)
    
    import_id = mapped_column(Integer, ForeignKey("import_calendar.import_id"))