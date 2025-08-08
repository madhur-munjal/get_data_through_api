from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# from src.schemas.tables.users import User


load_dotenv()  # ✅ This loads .env variables into os.environ
# Load environment variables from .env file
mysql_username = os.getenv("mysql_username")
mysql_password = os.getenv("mysql_password")
hostname = os.getenv("hostname")
database = os.getenv("database")
db_port = os.getenv("db_port")

print(f"mysql_username: {mysql_username}")
# SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{mysql_username}:{mysql_password}@{hostname}/{database}"
# DATABASE_URL = "mysql+mysqlconnector://root:root@db:3306/my_db"
DATABASE_URL = f"mysql+mysqlconnector://{mysql_username}:{mysql_password}@{hostname}:{db_port}/{database}"
print(f"DATABASE_URL: {DATABASE_URL}")
print("DATABASE_URL:", os.getenv("DATABASE_URL"))

engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"connect_timeout": 10})

# engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, connect_args={"connect_timeout": 10})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
Base1 = declarative_base()


def get_db():
    """

    :return:
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
