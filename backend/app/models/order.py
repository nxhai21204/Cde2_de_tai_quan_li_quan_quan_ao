from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database.base import Base

class PaymentStatus(str, enum.Enum):
    unpaid = "unpaid"
    paid = "paid"
    refunded = "refunded"

class UserOrderAction(str, enum.Enum):
    received = "received"
    return_requested = "return_requested"
    cancel_return_request = "cancel_return_request"

class OrderStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    shipped = "shipped"
    delivered = "delivered"
    received = "received"
    return_requested = "return_requested"
    refunded = "refunded"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    payment_method = Column(String, nullable=True)
    status = Column(
        String(30),
        nullable=False,
        default=OrderStatus.pending.value
    )
    payment_status = Column(String, default=PaymentStatus.unpaid.value)
    total_amount = Column(Float, default=0)
    shipping_address = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship với User
    user = relationship("app.models.user.User", back_populates="orders")

    # Relationship với OrderItem
    items = relationship(
        "app.models.order_item.OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )
