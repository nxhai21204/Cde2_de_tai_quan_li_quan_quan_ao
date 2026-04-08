from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


# ============================
# Product Schema (hiển thị trong Variant)
# ============================
class ProductInVariant(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


# ============================
# Variant Schema (hiển thị trong Inventory)
# ============================
class VariantInInventory(BaseModel):
    id: int
    size: str
    color: str
    stock: int
    product: ProductInVariant

    model_config = ConfigDict(from_attributes=True)


# ============================
# Inventory Create
# ============================
class InventoryCreate(BaseModel):
    stock: int = Field(..., ge=1)
    type: str = Field(..., pattern="^(IN|OUT)$")
    note: Optional[str] = None


# ============================
# Inventory Read (full info)
# ============================
class InventoryRead(BaseModel):
    id: int
    product_variant_id: int
    stock: int
    type: str
    note: Optional[str] = None
    created_at: datetime

    # đổi tên này
    product_variant: VariantInInventory

    model_config = ConfigDict(from_attributes=True)



# ============================
# Inventory Update (KHÔNG DÙNG)
# ============================

class InventoryUpdate(BaseModel):
    stock: int = Field(..., ge=0)
