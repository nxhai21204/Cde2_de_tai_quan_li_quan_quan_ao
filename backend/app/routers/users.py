# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.database.session import get_db
# Dùng các dependency đã định nghĩa trong app.core.security
from app.core.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/me", response_model=UserResponse, summary="Thông tin User hiện tại")
def read_current_user(current_user: User = Depends(get_current_user)):
    # Trả về UserResponse để lọc các trường nhạy cảm
    return current_user


# ✅ THÊM: CRUD cho User (chỉ Admin)
@router.get("/", response_model=list[UserResponse], summary="Lấy danh sách User (Admin)")
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(User).all()


@router.put("/{user_id}", response_model=UserResponse, summary="Cập nhật User (Admin)")
def update_user(
        user_id: int,
        user_data: UserUpdate,
        db: Session = Depends(get_db),
        admin: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xóa User (Admin)")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}