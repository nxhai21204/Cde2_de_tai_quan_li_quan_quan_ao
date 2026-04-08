from sqlalchemy.orm import Session
from .engine import SessionLocal

# Dependency FastAPI
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
