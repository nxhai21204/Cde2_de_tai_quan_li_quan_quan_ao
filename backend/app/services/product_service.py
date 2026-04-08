from sqlalchemy.orm import Session, joinedload
from typing import Optional, List

from app.models.product import Product, ProductImage
from app.models.product_variant import ProductVariant
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:

    # =========================================================
    # Lấy danh sách sản phẩm + variants
    # =========================================================
    def list(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 50,
        category_id: Optional[int] = None,
        q: Optional[str] = None,
        size: Optional[str] = None,
        color: Optional[str] = None
    ) -> List[Product]:

        qset = db.query(Product).options(
            joinedload(Product.variants),    # load tất cả biến thể
            joinedload(Product.images)       # load hình ảnh
        )

        if category_id:
            qset = qset.filter(Product.category_id == category_id)

        if q:
            qset = qset.filter(Product.name.ilike(f"%{q}%"))

        products = qset.offset(skip).limit(limit).all()

        # GIÁ BIẾN THỂ = GIÁ PRODUCT
        for p in products:
            for v in p.variants:
                v.price = p.price

        # Lọc theo thuộc tính variant
        if size or color:
            filtered = []
            for p in products:
                matched = False
                for v in p.variants:
                    if size and v.size != size:
                        continue
                    if color and v.color != color:
                        continue
                    matched = True
                    break
                if matched:
                    filtered.append(p)
            return filtered

        return products

    # =========================================================
    # Lấy chi tiết 1 sản phẩm
    # =========================================================
    def get(self, db: Session, product_id: int) -> Optional[Product]:
        product = (
            db.query(Product)
            .options(joinedload(Product.variants), joinedload(Product.images))
            .filter(Product.id == product_id)
            .first()
        )

        if product:
            for v in product.variants:
                v.price = product.price

        return product

    # =========================================================
    # Tạo sản phẩm (không tạo variant)
    # =========================================================
    def create(self, db: Session, data: ProductCreate):
        product_data = data.model_dump(exclude={"variants"}, exclude_none=True)
        product = Product(**product_data)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    # =========================================================
    # Update sản phẩm (không động đến variants)
    # =========================================================
    def update(self, db: Session, product_id: int, data: ProductUpdate):
        product = self.get(db, product_id)
        if not product:
            return None

        product_data = data.model_dump(
            exclude={"variants", "images"},
            exclude_unset=True
        )

        for k, v in product_data.items():
            setattr(product, k, v)

        db.commit()
        db.refresh(product)
        return product

    # =========================================================
    # Xóa sản phẩm
    # =========================================================
    def delete(self, db: Session, product_id: int):
        product = self.get(db, product_id)
        if not product:
            return False
        db.delete(product)
        db.commit()
        return True


product_service = ProductService()
