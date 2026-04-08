from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base

class InventoryLog(Base):
    __tablename__ = "inventory_log"

    id = Column(Integer, primary_key=True, index=True)

    product_variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=False)

    stock = Column(Integer, nullable=False)  # + nhập / - xuất
    type = Column(String, nullable=False)       # order, cancel, import
    note = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Optional: quan hệ nếu bạn muốn
    product_variant = relationship("ProductVariant", back_populates="inventory_logs")
