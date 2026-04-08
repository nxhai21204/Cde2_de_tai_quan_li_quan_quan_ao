# app/routers/product_variants.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.session import get_db
from app.core.dependencies import require_manager
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.inventory_log import InventoryLog

from app.schemas.product import ProductVariantCreate, ProductVariantRead

router = APIRouter(
    prefix="/api/v1",
    tags=["Product Variants"]
)

# ====================================================================
# Lấy danh sách biến thể theo product_id
# ====================================================================
@router.get("/products/{product_id}/variants", response_model=list[ProductVariantRead])
def list_variants_by_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product không tồn tại")
    return product.variants


# ====================================================================
# Tạo biến thể mới + nhập kho ban đầu (dùng stock)
# ====================================================================
@router.post(
    "/products/{product_id}/variants",
    response_model=ProductVariantRead,
    status_code=status.HTTP_201_CREATED
)
def create_variant(
    product_id: int,
    data: ProductVariantCreate,
    db: Session = Depends(get_db),
    manager=Depends(require_manager)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product không tồn tại")

    exists = (
        db.query(ProductVariant)
        .filter(
            ProductVariant.product_id == product_id,
            ProductVariant.size == data.size,
            ProductVariant.color == data.color,
        )
        .first()
    )
    if exists:
        raise HTTPException(400, "Biến thể size + color đã tồn tại")

    # Tạo variant với giá theo product
    variant = ProductVariant(
        product_id=product_id,
        size=data.size,
        color=data.color,
        stock=0,
        price=product.price
    )
    db.add(variant)
    db.flush()  # lấy variant.id

    # *** CẬP NHẬT STOCK + GHI LOG ***
    if data.stock > 0:
        # Ghi log
        log = InventoryLog(
            product_variant_id=variant.id,
            stock=data.stock,
            type="IN",
            note="Khởi tạo tồn kho"
        )
        db.add(log)

        # *** CẬP NHẬT STOCK BIẾN THỂ ***
        variant.stock += data.stock

    db.commit()
    db.refresh(variant)

    return variant



# ====================================================================
# Update biến thể (chỉ size/color)
# ====================================================================
@router.put("/variants/{variant_id}", response_model=ProductVariantRead)
def update_variant(
    variant_id: int,
    data: ProductVariantCreate,
    db: Session = Depends(get_db),
    manager=Depends(require_manager)
):
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(404, "Variant không tìm thấy")

    exists = (
        db.query(ProductVariant)
        .filter(
            ProductVariant.product_id == variant.product_id,
            ProductVariant.size == data.size,
            ProductVariant.color == data.color,
            ProductVariant.id != variant_id
        )
        .first()
    )
    if exists:
        raise HTTPException(400, "Biến thể size + color đã tồn tại")

    variant.size = data.size
    variant.color = data.color

    db.commit()
    db.refresh(variant)

    return variant


# ====================================================================
# Xóa biến thể + inventory log
# ====================================================================
@router.delete("/variants/{variant_id}", status_code=200)
def delete_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    admin_or_manager=Depends(require_manager)
):
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(404, "Variant không tìm thấy")

    db.query(InventoryLog).filter(InventoryLog.product_variant_id == variant_id).delete()

    db.delete(variant)
    db.commit()

    return {"message": "Variant deleted successfully"}
