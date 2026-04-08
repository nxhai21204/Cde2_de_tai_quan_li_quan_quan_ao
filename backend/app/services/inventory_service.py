from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.inventory import Inventory
from app.models.product_variant import ProductVariant
from app.schemas.inventory import InventoryCreate


class InventoryService:

    def create(self, db: Session, variant_id: int, data: InventoryCreate):

        variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
        if not variant:
            raise HTTPException(404, "Variant not found")

        # ====== Nhập kho ======
        if data.type == "IN":
            variant.stock += data.quantity

        # ====== Xuất kho ======
        elif data.type == "OUT":
            if variant.stock < data.quantity:
                raise HTTPException(400, "Not enough stock to export")
            variant.stock -= data.quantity

        else:
            raise HTTPException(400, "Invalid type (IN or OUT required)")

        # Lưu lịch sử
        inv = Inventory(
            product_variant_id=variant_id,
            quantity=data.quantity,
            type=data.type,
            note=data.note
        )

        db.add(inv)
        db.add(variant)
        db.commit()

        db.refresh(inv)
        db.refresh(variant)

        return inv

    def history(self, db: Session, variant_id: int):
        return db.query(Inventory).filter(
            Inventory.product_variant_id == variant_id
        ).order_by(Inventory.created_at.desc()).all()


inventory_service = InventoryService()
