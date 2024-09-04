from sqlalchemy import String, Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship

from config import Base

class ImportCalendar(Base):
    __tablename__ = "import_calendar"
    
    import_id = Column(Integer, primary_key=True, autoincrement=True)
    is_success = Column(Integer, default=1, nullable=False)
    event_count = Column(Integer, default=1, nullable=False)
    ics_file_path = Column(String)
    time_taken = Column(Float)
    fail_count = Column(Integer)
    
    calendar_id = Column(Integer, ForeignKey("calendars.calendar_id"))
    
    calendar = relationship("Calendars")
    

class FailedImportEvent(Base):
    __tablename__ = "failed_import_event"
    
    failed_import_event_id = Column(Integer, primary_key=True, autoincrement=True)
    log = Column(String(2047), nullable=False)
    
    import_id = Column(Integer, ForeignKey("import_calendar.import_id"))