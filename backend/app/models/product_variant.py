from sqlalchemy import Column, String, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database.base import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True)
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE")  # ✅ rất quan trọng
    )
    size = Column(String)
    color = Column(String)
    stock = Column(Integer, default=0)
    price = Column(Float, nullable=False)
    product = relationship("Product", back_populates="variants")

    # Một product_variant có nhiều bản ghi inventory log
    inventory_logs = relationship(
        "InventoryLog",
        back_populates="product_variant",
        lazy="select",
        cascade="all, delete-orphan"
    )
    order_items = relationship("OrderItem", back_populates="variant", cascade="all, delete-orphan")