from sqlalchemy import Column, Integer, String, DateTime, Date
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userName = Column(String, unique=True, nullable=False, index=True)
    passWordHash = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    lastLogin = Column(DateTime, nullable=True)
    skinType = Column(String, nullable=True)

    fullName = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    birthdate = Column(Date, nullable=False)
    phone = Column(String, nullable=False)