from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import Dict
from app.database.session import get_db
from app.core.security import decode_access_token
from app.models.user import User

router = APIRouter()
active_connections: Dict[int, WebSocket] = {}


# =========================
# Lấy user từ token WS
# =========================
async def get_user_from_ws(ws: WebSocket, db: Session) -> User | None:
    token = ws.query_params.get("token")
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    user_id = payload.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


# =========================
# WebSocket Chat
# =========================
@router.websocket("/api/v1/chat/ws")
async def chat_ws(ws: WebSocket, db: Session = Depends(get_db)):
    user = await get_user_from_ws(ws, db)

    if not user:
        await ws.close(code=1008)
        return

    await ws.accept()
    active_connections[user.id] = ws
    print(f"🔌 WS connected: {user.username} ({user.id})")

    try:
        while True:
            data = await ws.receive_json()

            to_id = data.get("to")
            content = data.get("content")

            if not to_id or not content:
                continue

            payload = {
                "from": user.id,
                "from_name": user.username,
                "content": content
            }

            # ✅ chỉ gửi cho người nhận, không gửi lại cho chính mình
            if to_id in active_connections and to_id != user.id:
                await active_connections[to_id].send_json(payload)

    except WebSocketDisconnect:
        print(f"❌ WS disconnected: {user.username}")
    finally:
        active_connections.pop(user.id, None)

