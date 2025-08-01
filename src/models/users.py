from sqlalchemy import Column, Integer, Text, String
from src.database import Base

# from sqlalchemy.ext.declarative import declarative_base
#
# Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, unique=True)  # index=True)
    password = Column(Text, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    address = Column(Text, nullable=True)
    contact_number = Column(Text, nullable=True)
