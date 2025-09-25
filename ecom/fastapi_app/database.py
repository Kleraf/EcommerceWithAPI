from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

"""
Configure SQLAlchemy to use the SAME SQLite DB as Django (db.sqlite3),
so FastAPI and Django share data.
"""

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DJANGO_DB_PATH = os.path.normpath(os.path.join(CURRENT_DIR, "..", "db.sqlite3"))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DJANGO_DB_PATH}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
