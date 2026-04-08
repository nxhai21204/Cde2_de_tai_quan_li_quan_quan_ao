# app/routers/products.py
from sqlalchemy.orm import joinedload
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from io import BytesIO
import uuid

from app.database.session import get_db
from app.schemas.product import ProductRead, ProductCreate
from app.core.dependencies import require_admin, require_manager
from app.services.product_service import product_service
from app.services.storage_service import storage_service
from app.models.product import Product, ProductImage

router = APIRouter(prefix="/api/v1/products", tags=["Products"])


# ================================================================
# Lấy danh sách sản phẩm
# ================================================================
@router.get("/", response_model=List[ProductRead])
def list_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
    category_id: Optional[int] = None,
    q: Optional[str] = None,
    size: Optional[str] = None,
    color: Optional[str] = None
):
    return product_service.list(
        db,
        skip=skip,
        limit=limit,
        category_id=category_id,
        q=q,
        size=size,
        color=color
    )


# ================================================================
# Lấy 1 sản phẩm theo ID
# ================================================================
@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = product_service.get(db, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product


# ================================================================
# Tạo sản phẩm — KHÔNG còn tạo biến thể tại đây
# ================================================================
@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category_id: int = Form(...),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    admin_or_manager=Depends(require_manager)
):
    # =====================
    # 1. CREATE PRODUCT
    # =====================
    payload_model = ProductCreate(
        name=name,
        description=description,
        price=price,
        category_id=category_id
    )

    product = product_service.create(db, payload_model)

    # =====================
    # 2. UPLOAD IMAGES
    # =====================
    if images:
        new_images = []

        for idx, img in enumerate(images):
            ext = img.filename.split(".")[-1].lower()

            if ext not in ["png", "jpg", "jpeg", "gif"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type: {img.filename}"
                )

            file_name = f"product-{product.id}-{uuid.uuid4()}.{ext}"
            data = BytesIO(await img.read())

            # ⚠️ KHÔNG content_type
            storage_service.upload_file(
                data,
                object_name=file_name
            )

            db_image = ProductImage(
                product_id=product.id,
                image_url=file_name,   # ✅ CHỈ filename
                is_main=(idx == 0)
            )

            db.add(db_image)
            new_images.append(db_image)

        # =====================
        # 3. SET THUMBNAIL
        # =====================
        if new_images:
            product.thumbnail = new_images[0].image_url
            db.add(product)

        db.commit()
        db.refresh(product)

    return product


# ================================================================
# Xóa sản phẩm (Admin)
# ================================================================
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    # Lấy sản phẩm + load variants + images
    product = (
        db.query(Product)
        .options(
            joinedload(Product.variants),
            joinedload(Product.images)
        )
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(404, "Product not found")

    # === 1. XÓA INVENTORY LIÊN QUAN TỚI TẤT CẢ VARIANTS ===
    variant_ids = [v.id for v in product.variants]
    if variant_ids:
        db.query(Inventory).filter(
            Inventory.product_variant_id.in_(variant_ids)
        ).delete(synchronize_session=False)

    # === 2. XÓA FILE ẢNH (MinIO / local) ===
    for img in product.images:
        try:
            storage_service.delete_file(object_name=img.image_url)
        except:
            pass  # không để crash

    # === 3. XÓA PRODUCT (tự xóa images + variants nhờ cascade) ===
    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}

