from sqlalchemy.orm import Session
from fastapi import HTTPException
from decimal import Decimal

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.inventory_log import InventoryLog
from app.models.product_variant import ProductVariant
from app.models.product import Product
from app.schemas.order import OrderRead, OrderItemRead

class OrderService:

    # ============================
    # TẠO ĐƠN HÀNG
    # ============================
    def create_order(self, db: Session, user_id: int, items: list):
        if not items:
            raise HTTPException(400, "Danh sách sản phẩm trống")

        variants = {}

        for it in items:
            if it.quantity <= 0:
                raise HTTPException(400, "Số lượng không hợp lệ")

            # 🔴 LOCK variant để tránh race condition
            variant = (
                db.query(ProductVariant)
                .filter(ProductVariant.id == it.product_variant_id)
                .with_for_update()
                .first()
            )

            if not variant:
                raise HTTPException(
                    status_code=404,
                    detail=f"Biến thể {it.product_variant_id} không tồn tại"
                )

            if variant.stock < it.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Hết hàng: {variant.size} - {variant.color}"
                )

            variants[it.product_variant_id] = variant

        # Tạo order
        order = Order(
            user_id=user_id,
            status="pending",
            payment_status="unpaid",
            payment_method="COD",
            total_amount=0
        )
        db.add(order)
        db.flush()

        total = 0
        for it in items:
            variant = variants[it.product_variant_id]
            variant.stock -= it.quantity
            total += variant.price * it.quantity

            db.add(OrderItem(
                order_id=order.id,
                product_variant_id=variant.id,
                price=variant.price,
                quantity=it.quantity
            ))

            db.add(InventoryLog(
                product_variant_id=variant.id,
                stock=-it.quantity,
                type="order",
                note=f"Order #{order.id}"
            ))

        order.total_amount = float(total)
        db.commit()
        db.refresh(order)
        return order

    # ============================
    # LẤY ĐƠN
    # ============================
    def get_order(self, db: Session, order_id: int):
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(404, "Order not found")
        return order

    # ============================
    # HỦY ĐƠN -> HOÀN KHO
    # ============================
    def cancel_order(self, db: Session, order_id: int):
        order = self.get_order(db, order_id)

        if order.status == "cancelled":
            raise HTTPException(400, "Đơn đã hủy trước đó")

        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

        for oi in order_items:
            variant = db.query(ProductVariant).filter(ProductVariant.id == oi.product_variant_id).first()
            if variant:
                variant.stock += oi.quantity
                log = InventoryLog(
                    product_variant_id=variant.id,
                    stock=oi.quantity,
                    type="cancel",
                    note=f"Cancel order {order.id}"
                )
                db.add(log)

        order.status = "cancelled"
        order.payment_status = "refunded"

        db.commit()
        db.refresh(order)

        return order

    # ============================
    # FORMAT CHO FRONTEND
    # ============================
    def get_order_detail_for_fe(self, db: Session, order_id: int) -> OrderRead:
        order = self.get_order(db, order_id)

        items_raw = (
            db.query(OrderItem, ProductVariant, Product)
            .join(ProductVariant, OrderItem.product_variant_id == ProductVariant.id)
            .join(Product, ProductVariant.product_id == Product.id)
            .filter(OrderItem.order_id == order.id)
            .all()
        )

        items = []
        for oi, variant, product in items_raw:
            items.append(OrderItemRead(
                id=oi.id,
                product_variant_id=variant.id,
                quantity=oi.quantity,
                price=float(oi.price),
                size=variant.size,
                color=variant.color,
                product_name=product.name,
                product_thumbnail=getattr(product, "thumbnail", None)
            ))

        return OrderRead(
            id=order.id,
            user_id=order.user_id,
            status=order.status,
            payment_status=order.payment_status,
            payment_method=order.payment_method,
            total_amount=float(order.total_amount),
            created_at=order.created_at,
            items=items
        )

    # ============================
    # HOÀN KHO NỘI BỘ
    # ============================
    def restore_stock(self, db: Session, order_id: int):
        items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        for item in items:
            variant = db.query(ProductVariant).filter(ProductVariant.id == item.product_variant_id).first()
            if variant:
                variant.stock += item.quantity
        db.commit()


order_service = OrderService()
