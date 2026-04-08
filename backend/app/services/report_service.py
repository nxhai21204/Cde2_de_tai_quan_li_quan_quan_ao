# app/services/report_service.py

from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc, literal_column
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product_variant import ProductVariant



class ReportService:
    def get_sales_by_period(self, db: Session, period: str = 'day'):
        """Thống kê doanh số theo ngày, tháng, hoặc năm."""

        # Ánh xạ chu kỳ thống kê sang hàm SQL
        if period == 'month':
            date_col = func.date_trunc('month', Order.created_at)
        elif period == 'year':
            date_col = func.date_trunc('year', Order.created_at)
        else:  # Mặc định là 'day'
            date_col = func.date_trunc('day', Order.created_at)

        # Truy vấn: Nhóm theo chu kỳ và tính tổng
        results = db.query(
            date_col.label('period_start'),
            func.count(Order.id).label('total_orders'),
            func.sum(Order.total_amount).label('total_sales')
        ).group_by('period_start').order_by('period_start').all()

        return [
            {
                "period": r.period_start.isoformat(),
                "total_orders": r.total_orders,
                "total_sales": r.total_sales
            }
            for r in results
        ]

    def get_top_selling_variants(self, db: Session, limit: int = 10, time_frame: str = 'year'):
        """Thống kê các Biến thể (ProductVariant) bán chạy nhất."""

        # Xác định khoảng thời gian cho truy vấn
        from datetime import datetime, timedelta
        if time_frame == 'month':
            start_date = datetime.now() - timedelta(days=30)
        elif time_frame == 'year':
            start_date = datetime.now() - timedelta(days=365)
        else:
            start_date = datetime.min  # Từ đầu

        # Truy vấn: JOIN OrderItem và ProductVariant, tính tổng số lượng bán được
        results = db.query(
            ProductVariant.id.label('variant_id'),
            ProductVariant.size,
            ProductVariant.color,
            ProductVariant.product_id,
            func.sum(OrderItem.quantity).label('total_quantity_sold')
        ).join(OrderItem, OrderItem.product_variant_id == ProductVariant.id) \
            .join(Order, Order.id == OrderItem.order_id) \
            .filter(Order.created_at >= start_date) \
            .group_by(
            ProductVariant.id,
            ProductVariant.size,
            ProductVariant.color,
            ProductVariant.product_id
        ).order_by(desc('total_quantity_sold')).limit(limit).all()

        # Dùng `model_dump()` nếu cần ánh xạ đầy đủ model ProductVariant
        return [
            {
                "variant_id": r.variant_id,
                "product_id": r.product_id,
                "size": r.size,
                "color": r.color,
                "total_quantity_sold": r.total_quantity_sold,
            }
            for r in results
        ]


report_service = ReportService()