from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


# ============================
# ITEM CREATE
# ============================
class OrderItemCreate(BaseModel):
    product_variant_id: int = Field(..., gt=0, description="ID biến thể hợp lệ")
    quantity: int = Field(..., gt=0, description="Số lượng > 0")

# ============================
# ORDER CREATE
# ============================
class OrderCreate(BaseModel):
    items: List[OrderItemCreate] = Field(..., min_items=1)

# ============================
# ITEM READ (Trả về cho FE)
# ============================
class OrderItemRead(BaseModel):
    id: int
    product_variant_id: int
    quantity: int
    price: float


    size: Optional[str] = None
    color: Optional[str] = None
    product_name: Optional[str] = None
    product_thumbnail: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ============================
# ORDER READ (Trả về cho FE)
# ============================
class OrderRead(BaseModel):
    id: int
    user_id: Optional[int] = None
    status: str
    payment_status: str
    payment_method: Optional[str] = None
    total_amount: float
    created_at: datetime

    items: List[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)


# ============================
# ORDER UPDATE STATUS
# ============================
class OrderUpdateStatus(BaseModel):
    status: str


# ============================
# ORDER UPDATE (Admin/Manager)
# ============================
class OrderUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Trạng thái mới của đơn hàng")
    shipping_address: Optional[str] = Field(None, description="Địa chỉ giao hàng")
    payment_status: Optional[str] = Field(None, description="Trạng thái thanh toán (paid/unpaid/refunded)")

    model_config = ConfigDict(from_attributes=True)
