# app/routers/order_item.py (Chỉ dành cho Admin/Quản lý)

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.order_item import OrderItem
from app.schemas.order_item import OrderItemCreate, OrderItemUpdate, OrderItemResponse
from app.core.dependencies import require_admin

# THAY ĐỔI: Đổi prefix thành /api/v1/order-items
router = APIRouter(prefix="/api/v1/order-items", tags=["OrderItems"])

# Create - Bảo mật Admin (Thường chỉ dùng nội bộ hoặc do OrderService tạo)
@router.post("/", response_model=OrderItemResponse, status_code=status.HTTP_201_CREATED)
def create_order_item(item: OrderItemCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    db_item = OrderItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# Read all - Bảo mật Admin
@router.get("/", response_model=List[OrderItemResponse])
def get_order_items(db: Session = Depends(get_db), admin=Depends(require_admin)):
    return db.query(OrderItem).all()

# Read one - Bảo mật Admin
@router.get("/{item_id}", response_model=OrderItemResponse)
def get_order_item(item_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    item = db.query(OrderItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OrderItem not found")
    return item

# Update - Bảo mật Admin
@router.put("/{item_id}", response_model=OrderItemResponse)
def update_order_item(item_id: int, item_data: OrderItemUpdate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    item = db.query(OrderItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OrderItem not found")
    for key, value in item_data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item

# Delete - Bảo mật Admin
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_item(item_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    item = db.query(OrderItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="OrderItem not found")
    db.delete(item)
    db.commit()
    return {"message": "OrderItem deleted successfully"}