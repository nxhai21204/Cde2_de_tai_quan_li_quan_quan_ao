from pydantic import EmailStr, BaseModel, ConfigDict
from typing import Optional, Literal
from app.schemas.auth import UserCreate, UserLogin, TokenSchema, RefreshRequest

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    # Chú ý: Admin/Manager chỉ nên được tạo bởi Admin, hoặc mặc định là 'user'
    role: Literal["user", "admin", "manager"] = "user"

class UserLogin(BaseModel):
    username_or_email: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[Literal["user", "admin", "manager"]] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer" # Mặc định là bearer