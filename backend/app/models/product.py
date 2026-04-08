# app/models/product.py
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base
import uuid
from app.models.mixins import TimestampMixin
from sqlalchemy.ext.hybrid import hybrid_property

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String, nullable=True)
    price = Column(Float)
    category_id = Column(Integer, ForeignKey("categories.id"))
    thumbnail = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),   # ✅ BẮT BUỘC
        onupdate=func.now(),
        nullable=False
    )
    category = relationship("Category", back_populates="products")

    variants = relationship(
        "ProductVariant",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    images = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    @property
    def main_image(self) -> str | None:
        if self.images:
            for img in self.images:
                if img.is_main:
                    return img.url
            return self.images[0].url
        return f"/static/uploads/{self.thumbnail}" if self.thumbnail else None

    @property
    def total_stock(self):
        return sum(v.stock for v in self.variants)


class ProductImage(Base, TimestampMixin):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    image_url = Column(String, nullable=False)
    is_main = Column(Boolean, default=False)

    product = relationship("Product", back_populates="images")

    @property
    def url(self) -> str:
        return f"/static/uploads/{self.image_url}" if self.image_url else ""

    @hybrid_property
    def total_stock(self):
        if self.product and self.product.variants:
            return sum(v.stock for v in self.product.variants)
        return 0
