from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ============================================
# Schema: Thống kê Doanh số theo chu kỳ
# ============================================
class SalesReport(BaseModel):
    period: str = Field(..., description="Thời điểm bắt đầu chu kỳ (ISO string)")
    total_orders: int = Field(..., description="Tổng số đơn hàng")
    total_sales: float = Field(..., description="Tổng doanh thu")

    model_config = {"from_attributes": True}


# ============================================
# Schema: Biến thể Sản phẩm bán chạy nhất
# ============================================
class TopSellingVariant(BaseModel):
    variant_id: int = Field(..., description="ID biến thể")
    product_id: int = Field(..., description="ID sản phẩm gốc")
    size: Optional[str] = Field(None, description="Kích thước (nếu có)")
    color: Optional[str] = Field(None, description="Màu sắc (nếu có)")
    total_quantity_sold: int = Field(..., description="Tổng số lượng đã bán")

    model_config = {"from_attributes": True}
