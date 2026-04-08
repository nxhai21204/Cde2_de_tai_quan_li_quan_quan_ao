from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from fastapi import HTTPException, status

class CategoryService:
    def create(self, db: Session, category_data: CategoryCreate):
        # Check trùng name
        existing = db.query(Category).filter(Category.name == category_data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category name already exists")

        category = Category(
            name=category_data.name,
            description=category_data.description
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    def get_all(self, db: Session):
        return db.query(Category).all()

    def get(self, db: Session, category_id: int):
        return db.query(Category).filter(Category.id == category_id).first()

    def update(self, db: Session, category_id: int, category_data: CategoryUpdate):
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return None
        if category_data.name:
            # Check trùng name khi update
            existing = db.query(Category).filter(Category.name == category_data.name, Category.id != category_id).first()
            if existing:
                raise HTTPException(status_code=400, detail="Category name already exists")
            category.name = category_data.name
        if category_data.description is not None:
            category.description = category_data.description
        db.commit()
        db.refresh(category)
        return category

    def delete(self, db: Session, category_id: int):
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return False
        db.delete(category)
        db.commit()
        return True

category_service = CategoryService()
