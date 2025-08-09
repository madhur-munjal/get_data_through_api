import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()  # ✅ This loads .env variables into os.environ
mysql_username = os.getenv("mysql_username")
mysql_password = os.getenv("mysql_password")
hostname = os.getenv("hostname")
database = os.getenv("database")
db_port = os.getenv("db_port")
print(f"db_port: {db_port}")  # For debugging purposes, remove in production
# DATABASE_URL = rf'{os.getenv("DATABASE_URL")}'
DATABASE_URL = f"mysql+mysqlconnector://{mysql_username}:{mysql_password}@{hostname}:{db_port}/{database}"
print(f"DATABASE_URL: {DATABASE_URL}")  # For debugging purposes, remove in production
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"connect_timeout": 10}, echo=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    """

    :return:
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
