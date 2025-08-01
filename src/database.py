from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

mysql_username = ""
mysql_password = ""
hostname = ""
database = ""

# SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{mysql_username}:{mysql_password}@{hostname}/{database}"
# DATABASE_URL = "mysql+mysqlconnector://root:root@db:3306/my_db"
DATABASE_URL = "mysql+mysqlconnector://root:hMexqxGfkWVcteODYFoQtWZfrzBFkKwn@mainline.proxy.rlwy.net:28684/railway"
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

    # function to create view
