from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi import Query
from app.models.product_variant import ProductVariant
from app.models.order import Order, OrderStatus, UserOrderAction
from app.schemas.order import OrderCreate, OrderRead, OrderUpdate
from app.database.session import get_db
from app.core.dependencies import require_active_user, require_manager
from app.services.order_service import order_service
from app.models.user import User


router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])


# ========================
# TẠO ĐƠN HÀNG
# ========================
@router.post("/", response_model=OrderRead)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_active_user)
):
    if not payload.items:
        raise HTTPException(400, "Giỏ hàng trống")

    try:
        order = order_service.create_order(db, user.id, payload.items)
        return order_service.get_order_detail_for_fe(db, order.id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(500, "Lỗi hệ thống khi tạo đơn")

# ========================
# XEM CHI TIẾT ĐƠN
# ========================
@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_active_user)
):
    order = order_service.get_order(db, order_id)

    if user.role == "user" and order.user_id != user.id:
        raise HTTPException(403, "Không có quyền xem đơn này")

    return order_service.get_order_detail_for_fe(db, order_id)


# ========================
# DANH SÁCH ĐƠN
# ========================
@router.get("/", response_model=List[OrderRead])
def list_orders(
    db: Session = Depends(get_db),
    user=Depends(require_active_user)
):
    if user.role in ["admin", "manager"]:
        orders = db.query(Order).all()
    else:
        orders = db.query(Order).filter(Order.user_id == user.id).all()

    return [order_service.get_order_detail_for_fe(db, o.id) for o in orders]


# ========================
# HỦY ĐƠN (USER + ADMIN)
# ========================
@router.put("/{order_id}/cancel", response_model=OrderRead)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_active_user)
):
    order = order_service.get_order(db, order_id)

    if user.role == "user":
        if order.user_id != user.id:
            raise HTTPException(403, "Không có quyền")
        if order.status not in ["pending"]:
            raise HTTPException(400, "User chỉ được hủy đơn pending")

    order_service.cancel_order(db, order_id, user)
    return order_service.get_order_detail_for_fe(db, order_id)


# ========================
# XÁC NHẬN GIAO HÀNG
# ========================
@router.put("/{order_id}/deliver", response_model=OrderRead)
def deliver_order(
    order_id: int,
    db: Session = Depends(get_db),
    manager=Depends(require_manager)
):
    order = order_service.get_order(db, order_id)

    if order.status not in ["confirmed", "shipping"]:
        raise HTTPException(400, "Không thể giao đơn ở trạng thái này")

    order.status = "delivered"
    order.payment_status = "paid"

    db.commit()
    db.refresh(order)

    return order_service.get_order_detail_for_fe(db, order.id)


# ========================
# ĐỔI PHƯƠNG THỨC THANH TOÁN
# ========================
@router.put("/{order_id}/payment-method", response_model=OrderRead)
def update_payment_method(
    order_id: int,
    method: str,
    db: Session = Depends(get_db),
    user=Depends(require_active_user)
):
    if method not in ["COD", "MOMO", "VNPAY"]:
        raise HTTPException(400, "Phương thức không hợp lệ")

    order = order_service.get_order(db, order_id)

    if order.user_id != user.id:
        raise HTTPException(403, "Không có quyền đổi")

    if order.status != "pending":
        raise HTTPException(400, "Chỉ đổi khi đơn pending")

    order.payment_method = method
    db.commit()
    db.refresh(order)

    return order_service.get_order_detail_for_fe(db, order_id)

# ========================
# ADMIN CẬP NHẬT TRẠNG THÁI ĐƠN HÀNG
# ========================
@router.put("/{order_id}/status", response_model=OrderRead)
def admin_update_status(
    order_id: int,
    status: OrderStatus = Query(...),
    db: Session = Depends(get_db),
    manager=Depends(require_manager)
):
    order = order_service.get_order(db, order_id)
 # Lấy từ DB
    current = order.status

    # 1. Cập nhật luồng hợp lệ (Flow)
    valid_flow = {
        "pending": ["confirmed", "cancelled"],
        "confirmed": ["shipped", "cancelled"],
        "shipped": ["delivered", "cancelled"],
        "delivered": ["received", "return_requested", "cancelled"],
        "received": ["return_requested"],
        "return_requested": ["refunded", "delivered"], # Duyệt hoàn tiền hoặc từ chối quay về delivered
        "refunded": [],
        "cancelled": []
    }

    if status.value not in valid_flow.get(current, []):
        raise HTTPException(400, f"Quy trình không hợp lệ: {current} -> {status.value}")

    # 2. Xử lý logic nghiệp vụ đặc biệt
    if status == OrderStatus.refunded:
        # Chuyển trạng thái thanh toán
        order.payment_status = "refunded"
        # Tự động hoàn kho hàng
        order_service.restore_stock(db, order_id)
        # Ghi chú hệ thống
        order.admin_note = "Hệ thống: Đã hoàn tiền và nhập lại kho."

    if status == OrderStatus.cancelled:
        order_service.restore_stock(db, order_id)

    order.status = status.value
    db.commit()
    db.refresh(order)
    return order_service.get_order_detail_for_fe(db, order.id)

@router.put("/{order_id}/user-status", response_model=OrderRead)
def user_update_order_status(
    order_id: int,
    action: UserOrderAction = Query(...),
    note: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_active_user)
):
    order = order_service.get_order(db, order_id)

    if order.user_id != user.id:
        raise HTTPException(403, "Không có quyền")

    # USER chỉ được gửi yêu cầu
    if action == UserOrderAction.received:
        if order.status != OrderStatus.delivered:
            raise HTTPException(400, "Đơn chưa giao")
        order.user_received_requested = True

    elif action == UserOrderAction.return_requested:
        if order.status != OrderStatus.delivered:
            raise HTTPException(400, "Chỉ yêu cầu trả sau khi giao")
        order.user_return_requested = True
        order.user_note = note

    elif action == UserOrderAction.cancel_return_request:
        if not order.user_return_requested:
            raise HTTPException(400, "Không có yêu cầu để hủy")
        order.user_return_requested = False
        order.user_note = None

    db.commit()
    db.refresh(order)

    return order_service.get_order_detail_for_fe(db, order.id)



