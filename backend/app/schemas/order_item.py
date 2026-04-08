# app/schemas/order_item.py

from pydantic import BaseModel, ConfigDict
from typing import Optional

# --- Dùng để tạo Order (chỉ cần variant_id và quantity) ---
class OrderItemCore(BaseModel):
    product_variant_id: int # ✅ THAY ĐỔI: Dùng product_variant_id
    quantity: int
    # Không cần price ở đây, sẽ lấy từ DB/Service

# --- Dùng cho CRUD riêng (Admin) ---
class OrderItemCreate(BaseModel):
    order_id: int
    product_variant_id: int # ✅ THAY ĐỔI: Dùng product_variant_id
    quantity: int
    price: float # Giá tại thời điểm đặt hàng

class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = None
    price: Optional[float] = None

# --- Schema trả về ---
class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_variant_id: int # ✅ THAY ĐỔI: Dùng product_variant_id
    quantity: int
    price: float

    model_config = ConfigDict(from_attributes=True)