from sqlalchemy import String, Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship, mapped_column

from config import Base

class ColorSet(Base):
    __tablename__ = "color_set"
    
    color_set_id = mapped_column(Integer, primary_key=True)
    color_name = mapped_column(String(20), nullable=True)
    hex_code = mapped_column(String(20), nullable=True)

class Calendars(Base):
    __tablename__ = "calendars"
    
    calendar_id = mapped_column(Integer, primary_key=True)
    timezone_id = mapped_column(String(20))
    created_at = mapped_column(DateTime, default=func.now())
    updated_at = mapped_column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    title = mapped_column(String(50), nullable=False)
    description = mapped_column(String(255), nullable=True)
    is_deleted = mapped_column(Integer, nullable=False, default=0)
    prod_id = mapped_column(String(255), nullable=False)
    
    #TODO color_set 값 로직 정하기
    color_set_id = mapped_column(Integer, ForeignKey("color_set.color_set_id"), default=1)
    user_id = mapped_column(Integer, ForeignKey("user.user_id"))
    
    color_set = relationship("ColorSet")
    user = relationship("User")