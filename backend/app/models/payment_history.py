# app/models/payment_history.py
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Text
from sqlalchemy.sql import func
from app.database.base import Base

class PaymentHistory(Base):
    __tablename__ = "payment_history"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    old_status = Column(String(50))
    new_status = Column(String(50))
    note = Column(Text)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
