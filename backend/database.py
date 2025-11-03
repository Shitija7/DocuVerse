# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

is_sqlite = DATABASE_URL.startswith("sqlite")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if is_sqlite else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
