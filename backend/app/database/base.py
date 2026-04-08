# app/database/base.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:02122004@localhost:5432/quan_ao_db"

# Tạo engine
engine = create_engine(DATABASE_URL, echo=True)  # echo=True để debug SQL

# Base class cho models
Base = declarative_base()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
