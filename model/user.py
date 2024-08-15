from enum import Enum as PEnum

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, Float, Enum
from sqlalchemy.orm import relationship

from config import Base

class Gender(PEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class AccountLink(Base):
    __tablename__ = "account_link"
    
    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True,)
    microsoft = Column(String)
    google = Column(String)
    
    user = relationship("User", back_populates="account_link", uselist=False)

class User(Base):
    __tablename__ = "user"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255),  nullable=False, unique=True)
    user_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    password = Column(String(255), nullable=True)
    gender = Column(Enum(Gender), nullable=True)
    phone_number = Column(String(20), nullable=True)
    role = Column(String(20), nullable=False)
    
    account_link = relationship("AccountLink", back_populates="user")