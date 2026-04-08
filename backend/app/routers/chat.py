from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import or_, and_

from app.routers.chat_ws import active_connections
from app.database.session import get_db
from app.schemas.chat import ChatCreate, ChatRead
from app.models.chat_message import ChatMessage
from app.models.user import User
from app.core.security import get_current_user
from app.core.dependencies import require_admin

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


# ==========================
# Hàm bổ trợ: Lấy lịch sử chat
# ==========================
def _get_history(db: Session, me: User, user_id: int, order_id: int | None = None):
    q = db.query(ChatMessage).filter(
        or_(
            and_(ChatMessage.sender_id == me.id, ChatMessage.receiver_id == user_id),
            and_(ChatMessage.sender_id == user_id, ChatMessage.receiver_id == me.id),
        )
    )

    if order_id:
        q = q.filter(ChatMessage.order_id == order_id)

    msgs = q.order_by(ChatMessage.created_at).all()

    return [
        ChatRead(
            id=m.id,
            sender_id=m.sender_id,
            sender_name=m.sender.username if m.sender else "",
            receiver_id=m.receiver_id,
            content=m.content,
            order_id=m.order_id,
            created_at=m.created_at
        )
        for m in msgs
    ]


# ==========================
# 1. LẤY LỊCH SỬ CHAT (Sửa lỗi 405)
# ==========================
@router.get("/", response_model=List[ChatRead])
def get_my_chat_history(
        user_id: int | None = None,
        order_id: int | None = None,
        db: Session = Depends(get_db),
        me: User = Depends(get_current_user)
):
    """
    Route chính để Frontend lấy lịch sử.
    - Nếu là User: Tự động lấy chat với Admin đầu tiên.
    - Nếu là Admin: Lấy chat với user_id được chỉ định.
    """
    if me.role != "admin":
        # Khách hàng luôn chat với admin
        admin = db.query(User).filter(User.role == "admin").first()
        target_id = admin.id if admin else 1  # Mặc định là ID 1 nếu chưa có admin
    else:
        # Admin phải truyền user_id muốn xem
        target_id = user_id

    if not target_id:
        raise HTTPException(status_code=400, detail="Thiếu user_id để lấy lịch sử")

    return _get_history(db, me, target_id, order_id)


# ==========================
# 2. GỬI TIN NHẮN QUA HTTP (Dùng làm fallback)
# ==========================
@router.post("/", response_model=ChatRead)
def send_message(payload: ChatCreate, db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    if me.role != "admin":
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        receiver_id = admin.id
    else:
        receiver_id = payload.receiver_id

    msg = ChatMessage(
        sender_id=me.id,
        receiver_id=receiver_id,
        content=payload.content,
        order_id=payload.order_id
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


# ==========================
# 3. CÁC ROUTE CHO ADMIN
# ==========================
@router.get("/admin/conversations", dependencies=[Depends(require_admin)])
def admin_conversations(db: Session = Depends(get_db), me: User = Depends(get_current_user)):
    # Lấy danh sách những người đã từng nhắn tin với Admin
    users = db.query(User).join(
        ChatMessage,
        or_(ChatMessage.sender_id == User.id, ChatMessage.receiver_id == User.id)
    ).filter(
        User.id != me.id,
        or_(ChatMessage.sender_id == me.id, ChatMessage.receiver_id == me.id)
    ).distinct().all()

    return [{"id": u.id, "username": u.username} for u in users]


@router.get("/online-users")
def online_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "manager"]:
        return []
    user_ids = list(active_connections.keys())
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    return [{"id": u.id, "username": u.username} for u in users]