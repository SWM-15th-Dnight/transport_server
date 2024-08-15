from sqlalchemy import String, Column, Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

from config import Base

from .user import User

class ColorSet(Base):
    __tablename__ = "color_set"
    
    color_set_id = Column(Integer, primary_key=True)
    color_name = Column(String(20), nullable=True)
    hex_code = Column(String(20), nullable=True)

class Calendar(Base):
    __tablename__ = "calendars"
    
    calendar_id = Column(Integer, primary_key=True)
    timezone_id = Column(String(20))
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    title = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    is_deleted = Column(Integer, nullable=False)
    
    color_set_id = Column(Integer, ForeignKey("color_set.color_set_id"))
    user_id = Column(Integer, ForeignKey("user.user_id"))
    
    color_set = relationship("ColorSet")
    user = relationship("User")