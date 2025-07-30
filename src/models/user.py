from sqlalchemy import Column, Integer, String, Text
from src.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(Text, nullable=True) #String, unique=True, index=True)
    password = Column(Text, nullable=True) #String)
