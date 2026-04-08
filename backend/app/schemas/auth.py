# app/schemas/auths.py
from pydantic import BaseModel, EmailStr
from typing import Literal, Optional

# =============================
# Request để đăng ký user
# =============================
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    # Chú ý: Admin/Manager chỉ nên được tạo bởi Admin, mặc định là 'user'
    role: Literal["user", "admin", "manager"] = "user"

# =============================
# Request để login
# =============================
class UserLogin(BaseModel):
    username_or_email: str
    password: str

# =============================
# Request để refresh token
# =============================
class RefreshRequest(BaseModel):
    user_id: int
    refresh_token: str

# =============================
# Response trả về thông tin user
# =============================
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        orm_mode = True  # Để có thể trả về từ SQLAlchemy

# =============================
# Response trả về token
# =============================
class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: int

