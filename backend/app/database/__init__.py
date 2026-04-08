# app/database/__init__.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# --- Cấu hình PostgreSQL ---
DB_USER = os.getenv("DB_USER", "postgres")         # user PostgreSQL
DB_PASSWORD = os.getenv("DB_PASSWORD", "02122004") # mật khẩu PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost")        # host
DB_PORT = os.getenv("DB_PORT", "5432")             # port
DB_NAME = os.getenv("DB_NAME", "quan_ao_db")      # tên database

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- Engine và Session ---
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)  # echo=True để log SQL

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Base class cho các models ---
Base = declarative_base()

# --- Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
