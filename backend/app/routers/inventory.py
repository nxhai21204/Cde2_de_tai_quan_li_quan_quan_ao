from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.inventory import InventoryCreate, InventoryRead
from app.database.session import get_db
from app.core.dependencies import require_admin

from app.models.inventory_log import InventoryLog
from app.models.product_variant import ProductVariant

router = APIRouter(
    prefix="/api/v1/inventory",
    tags=["Inventory Log"]
)

# ===========================
# LẤY TOÀN BỘ LỊCH SỬ XUẤT/NHẬP
# ===========================
@router.get("/", response_model=List[InventoryRead])
def get_all_inventory(db: Session = Depends(get_db), admin=Depends(require_admin)):
    return db.query(InventoryLog).order_by(InventoryLog.id.desc()).all()


# ===========================
# LẤY 1 LOG
# ===========================
@router.get("/{inventory_id}", response_model=InventoryRead)
def get_inventory(inventory_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    record = db.query(InventoryLog).filter(InventoryLog.id == inventory_id).first()
    if not record:
        raise HTTPException(404, "Inventory record not found")
    return record


# ===========================
# NHẬP KHO  (IN)
# ===========================
@router.post("/import/{variant_id}", response_model=InventoryRead)
def inventory_import(
    variant_id: int,
    data: InventoryCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(404, "Variant not found")

    if data.type != "IN":
        raise HTTPException(400, "For import stock, type must be 'IN'")

    if data.stock <= 0:
        raise HTTPException(400, "Stock must be > 0")

    # tăng tồn kho
    variant.stock += data.stock
    db.add(variant)

    # ghi log
    record = InventoryLog(
        product_variant_id=variant_id,
        stock=data.stock,
        type="IN",
        note=data.note
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ===========================
# XUẤT KHO (OUT)
# ===========================
@router.post("/export/{variant_id}", response_model=InventoryRead)
def inventory_export(
    variant_id: int,
    data: InventoryCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(404, "Variant not found")

    if data.type != "OUT":
        raise HTTPException(400, "For export stock, type must be 'OUT'")

    if data.stock <= 0:
        raise HTTPException(400, "Stock must be > 0")

    if variant.stock < data.stock:
        raise HTTPException(400, "Không đủ hàng trong kho")

    # giảm tồn kho
    variant.stock -= data.stock
    db.add(variant)

    # ghi log
    record = InventoryLog(
        product_variant_id=variant_id,
        stock=data.stock,
        type="OUT",
        note=data.note
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ===========================
# XÓA LOG
# ===========================
@router.delete("/{inventory_id}", status_code=204)
def delete_inventory(inventory_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    record = db.query(InventoryLog).filter(InventoryLog.id == inventory_id).first()
    if not record:
        raise HTTPException(404, "Inventory record not found")

    db.delete(record)
    db.commit()
