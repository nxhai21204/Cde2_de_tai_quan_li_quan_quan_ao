from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.mixins import TimestampMixin

class User(TimestampMixin, Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String(20), default="user")  # user, admin, manager
    is_active = Column(Boolean, default=True)

    # Quan hệ 1:n với orders
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

    # Quan hệ 1:1 với cart
    cart = relationship("Cart", back_populates="user", uselist=False)

    # Quan hệ 1:n với refresh tokens
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan"
    )
