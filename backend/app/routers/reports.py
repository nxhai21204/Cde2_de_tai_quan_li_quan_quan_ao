from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.core.dependencies import require_admin   # hoặc require_manager
from app.services.report_service import report_service
from app.schemas.report import SalesReport, TopSellingVariant


router = APIRouter(
    prefix="/api/v1/reports",
    tags=["Reports"],
    dependencies=[Depends(require_admin)]   # nếu muốn admin + manager thì đổi thành require_manager
)


# =========================
# THỐNG KÊ DOANH SỐ
# =========================
@router.get(
    "/sales",
    response_model=List[SalesReport],
    summary="Thống kê doanh số theo ngày, tháng, năm"
)
def get_sales_report(
    period: str = Query("day", description="Chu kỳ: 'day', 'month', 'year'"),
    db: Session = Depends(get_db)
):
    if period not in ["day", "month", "year"]:
        raise HTTPException(
            status_code=400,
            detail="Chu kỳ không hợp lệ. Chỉ chấp nhận 'day', 'month', 'year'."
        )

    return report_service.get_sales_by_period(db, period=period)


# =========================
# SẢN PHẨM BÁN CHẠY
# =========================
@router.get(
    "/top-selling",
    response_model=List[TopSellingVariant],
    summary="Danh sách các biến thể sản phẩm bán chạy nhất"
)
def get_top_selling_report(
    limit: int = Query(10, ge=1, description="Số lượng item top"),
    time_frame: str = Query("year", description="Khung thời gian: 'month', 'year', 'all'"),
    db: Session = Depends(get_db)
):
    if time_frame not in ["month", "year", "all"]:
        raise HTTPException(
            status_code=400,
            detail="Khung thời gian không hợp lệ. Chỉ chấp nhận 'month', 'year', 'all'."
        )

    return report_service.get_top_selling_variants(db, limit=limit, time_frame=time_frame)
