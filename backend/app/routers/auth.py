# app/routers/auths.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, UserResponse, TokenSchema, RefreshRequest
from app.services.auth_service import (
    register_user,
    authenticate_user,
    create_user_token,
    verify_refresh_token,
    create_refresh_token,
)

# --- Router ---
router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

# --- Register ---
@router.post("/register", response_model=UserResponse, summary="Đăng ký tài khoản")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Đăng ký tài khoản mới.
    Role mặc định là 'user' nếu không được chỉ định.
    """
    user = register_user(
        db,
        username=payload.username,
        email=payload.email,
        password=payload.password,
        role=payload.role
    )
    return user

# --- Refresh token ---
@router.post("/refresh", summary="Làm mới access token")
def refresh(rq: RefreshRequest, db: Session = Depends(get_db)):
    """
    Kiểm tra refresh token hợp lệ và trả về access token mới.
    """
    if not verify_refresh_token(db, rq.user_id, rq.refresh_token):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.get(User, rq.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = create_user_token(user)
    new_refresh = create_refresh_token(db, user)
    return {"access_token": access_token, "refresh_token": new_refresh}

# --- Login ---
@router.post("/login", summary="Đăng nhập")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username_or_email, payload.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Sai username/email hoặc password"
        )

    access_token = create_user_token(user)
    refresh_token = create_refresh_token(db, user)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user.id
    }

