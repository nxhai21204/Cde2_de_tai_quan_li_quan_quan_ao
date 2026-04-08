from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.core.dependencies import require_admin
from app.services.category_service import category_service

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])

# Create (Admin)
@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category_data: CategoryCreate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    return category_service.create(db, category_data)

# Read all (Public)
@router.get("/", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return category_service.get_all(db)

# Read one (Public)
@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = category_service.get(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

# Update (Admin)
@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category_data: CategoryUpdate, db: Session = Depends(get_db), admin=Depends(require_admin)):
    updated = category_service.update(db, category_id, category_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated

# Delete (Admin)
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    success = category_service.delete(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}
