from pydantic import BaseModel, Field
from typing import List

# =========================
# INPUT SCHEMA
# =========================

class CartItemCreate(BaseModel):
    product_variant_id: int = Field(..., gt=0, description="ID biến thể sản phẩm")
    quantity: int = Field(..., gt=0, description="Số lượng phải > 0")

CartItemAdd = CartItemCreate


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0, description="Số lượng phải > 0")


# =========================
# OUTPUT SCHEMA
# =========================

class CartItemResponse(BaseModel):
    id: int
    product_variant_id: int
    product_name: str  # tên sản phẩm
    size: str  # size của variant
    color: str
    quantity: int
    price: float
    subtotal: float

    class Config:
        orm_mode = True


class CartResponse(BaseModel):
    id: int                 # ✅ INT – KHÔNG UUID
    items: List[CartItemResponse]
    total: float

    class Config:
        orm_mode = True
