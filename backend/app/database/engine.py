from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

from app.core.config import settings

# Tạo engine kết nối PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    echo=False  # <-- tắt log SQL, dùng logging riêng nếu cần
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Logging SQLAlchemy ---
logging.basicConfig()
# Chỉ in WARNING trở lên cho engine SQL
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)