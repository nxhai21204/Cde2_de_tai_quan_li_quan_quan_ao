# app/models/payment.py
from sqlalchemy import Column, Integer, ForeignKey, Numeric, String, DateTime
from sqlalchemy.sql import func
from app.database.base import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    method = Column(String(50), nullable=False)   # cod, momo, vnpay, paypal, bank
    amount = Column(Numeric(12,2), nullable=False)
    status = Column(String(30), nullable=False, default="pending")  # pending, success, failed, refunded
    transaction_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
