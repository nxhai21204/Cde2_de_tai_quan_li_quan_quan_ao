from pydantic import BaseModel
from typing import Optional, List

# ================================
# Schema sản phẩm trong Category
# ================================
class ProductInCategory(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        orm_mode = True

# ================================
# Schema Category trả về
# ================================
class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    products: List[ProductInCategory] = []

    class Config:
        orm_mode = True

# ================================
# Schema tạo Category
# ================================
class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

# ================================
# Schema update Category
# ================================
class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
