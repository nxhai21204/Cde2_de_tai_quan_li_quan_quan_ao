from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class ProductVariantCreate(BaseModel):
    size: str = Field(..., description="Kích thước")
    color: str = Field(..., description="Màu")
    stock: int = Field(0, ge=0, description="Số lượng khởi tạo")


class ProductVariantRead(BaseModel):
    id: int
    product_id: int
    size: str
    color: str
    stock: int
    price: float

    class Config:
        orm_mode = True


class ProductImageCreate(BaseModel):
    image_url: str
    is_main: Optional[bool] = False

class ProductImageRead(BaseModel):
    id: int
    url: str
    is_main: bool

    model_config = ConfigDict(from_attributes=True)

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: int
    images: List[ProductImageCreate] = []

class ProductRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    category_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    main_image: Optional[str]
    images: List[ProductImageRead]
    variants: List[ProductVariantRead]
    total_stock: int

    model_config = ConfigDict(from_attributes=True)


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    variants: Optional[List[ProductVariantCreate]] = None
    images: Optional[List[ProductImageCreate]] = None
