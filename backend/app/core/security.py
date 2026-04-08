# app/core/security.py

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# import Security để sử dụng cho Bearer scheme
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.database.engine import SessionLocal
from app.models.user import User
# import settings từ app.core.config để đọc cấu hình
from app.core.config import settings

# =========================
# CONFIG
# =========================
# Các hằng số cấu hình được thay thế bằng settings.XXX
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()


# =========================
# DATABASE DEPENDENCY
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# PASSWORD FUNCTIONS
# =========================
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


# =========================
# JWT FUNCTIONS
# =========================
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    # 💡 Lấy thời gian hết hạn từ settings
    expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=expire_minutes))
    to_encode.update({"exp": expire})

    # 💡 Lấy SECRET_KEY và ALGORITHM từ settings
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        # 💡 Lấy SECRET_KEY và ALGORITHM từ settings
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        # Bắt lỗi khi token hết hạn hoặc không hợp lệ
        return None


# =========================
# USER DEPENDENCIES
# =========================
def get_current_user(
        # 💡 Dùng Security thay vì Depends
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
        db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials (Token invalid or expired)",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 💡 FIX LỖI: Kiểm tra và đọc key "user_id"
    user_id = payload.get("user_id") if payload else None

    if user_id is None:
        raise credentials_exception

    try:
        user_id = int(user_id)
    except ValueError:
        raise credentials_exception  # Token payload malformed

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # Trả về lỗi chung để tránh lộ thông tin user
        raise credentials_exception

    return user


