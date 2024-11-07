from enum import Enum as PEnum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import relationship, mapped_column

from config import Base

class Gender(PEnum):
    male = "male"
    female = "female"


class AccountLink(Base):
    __tablename__ = "account_link"
    
    user_id = mapped_column(Integer, ForeignKey("user.user_id"), primary_key=True,)
    microsoft = mapped_column(String)
    google = mapped_column(String)
    
    user = relationship("User", back_populates="account_link", uselist=False)

class User(Base):
    __tablename__ = "user"
    
    user_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    email = mapped_column(String(255),  nullable=False, unique=True)
    user_name = mapped_column(String(50), nullable=False)
    created_at = mapped_column(DateTime, default=func.current_timestamp())
    updated_at = mapped_column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    password = mapped_column(String(255), nullable=True)
    gender = mapped_column(Enum(Gender), nullable=True)
    phone_number = mapped_column(String(20), nullable=True)
    role = mapped_column(String(20), nullable=False)
    
    account_link = relationship("AccountLink", back_populates="user")