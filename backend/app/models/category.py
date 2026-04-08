from sqlalchemy import Column, Integer, String
from app.database.base import Base
from app.models.mixins import TimestampMixin
from sqlalchemy.orm import relationship

class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    # Đổi từ UUID sang int
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String, nullable=True)

    # Relationship với Product
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")
