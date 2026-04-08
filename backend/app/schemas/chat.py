from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ChatCreate(BaseModel):
    receiver_id: int
    content: str
    order_id: Optional[int] = None


class ChatRead(BaseModel):
    id: int
    sender_id: int
    sender_name: str
    receiver_id: int
    content: str
    order_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
