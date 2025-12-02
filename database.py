from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Creates a local SQLite database file
# SQLALCHEMY_DATABASE_URL = "sqlite:///./emt.db"

# MySQL Connection
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:641364@localhost/emt_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
