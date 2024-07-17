import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

abpwd = str(os.getenv('ABPWD', default=None))
SQLALCHEMY_DATABASE_URL = f"postgresql://aberdeen:{abpwd}@localhost:5432/instai"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = Session(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
