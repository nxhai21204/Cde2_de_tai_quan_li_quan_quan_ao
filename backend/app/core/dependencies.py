from fastapi import Depends, HTTPException, status
from app.models.user import User
from app.core.security import get_current_user # Giả định get_current_user nằm trong app.core.security

# Đây là hàm đã có sẵn (hoặc nên có) trong app/core/security
def require_active_user(current_user: User = Depends(get_current_user)) -> User:
    # Logic kiểm tra user có hoạt động không (thường được thực hiện trong get_current_user)
    return current_user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn phải là quản trị viên (Admin) để thực hiện hành động này."
        )
    return current_user

def require_manager(current_user: User = Depends(get_current_user)) -> User:
    # Cho phép Admin hoặc Manager
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn phải là quản trị viên (Admin) hoặc quản lý (Manager) để thực hiện hành động này."
        )
    return current_user