# app/services/auth_service.py
import secrets, hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.core.security import hash_password, verify_password, create_access_token

REFRESH_DAYS = 30

# --- Refresh token functions ---
def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()

def create_refresh_token(db: Session, user: User):
    raw = secrets.token_urlsafe(48)
    hashed = hash_token(raw)
    expires = datetime.utcnow() + timedelta(days=REFRESH_DAYS)
    rt = RefreshToken(user_id=user.id, token=hashed, expires_at=expires)
    db.add(rt); db.commit(); db.refresh(rt)
    return raw

def verify_refresh_token(db: Session, user_id:int, raw_token:str):
    hashed = hash_token(raw_token)
    rt = db.query(RefreshToken).filter(RefreshToken.user_id==user_id, RefreshToken.token==hashed).first()
    if not rt or rt.expires_at < datetime.utcnow():
        return False
    return True

# --- User functions ---
def register_user(db: Session, username: str, password: str, email: str, role: str = "user"):
    hashed_pw = hash_password(password)
    user = User(
        username=username,
        hashed_password=hashed_pw,
        email=email,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username==username).first()
    if not user or not verify_password(password, user.hashed_password):  # dùng hashed_password
        return None
    return user

def create_user_token(user: User):
    return create_access_token({"user_id": user.id})
