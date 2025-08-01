from sqlalchemy import Column, Integer, Text
# from src.database import Base

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(Text, nullable=True)  # String, unique=True, index=True)
    password = Column(Text, nullable=True)  # String)
    address = Column(Text, nullable=True)
    contact_number = Column(Text, nullable=True)
