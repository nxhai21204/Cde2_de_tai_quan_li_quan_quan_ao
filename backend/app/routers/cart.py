from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.checkout import CheckoutRequest
from app.database.session import get_db
from app.services.cart_service import cart_service
from app.schemas.cart import (
    CartItemAdd,
    CartItemUpdate,
    CartResponse
)
from app.core.dependencies import require_active_user as require_user

router = APIRouter(prefix="/api/v1/cart", tags=["Cart"])


@router.post("/items", response_model=CartResponse)
def add_item_to_cart(
    item: CartItemAdd,
    db: Session = Depends(get_db),
    user=Depends(require_user)
):
    cart_service.add_item(
        db=db,
        user_id=user.id,
        product_variant_id=item.product_variant_id,
        quantity=item.quantity
    )
    return cart_service.get_cart(db, user.id)


@router.get("/", response_model=CartResponse)
def get_cart(
    db: Session = Depends(get_db),
    user=Depends(require_user)
):
    return cart_service.get_cart(db, user.id)


@router.put("/items/{item_id}", response_model=CartResponse)
def update_item(
    item_id: int,
    payload: CartItemUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_user)
):
    try:
        cart_service.update_item_quantity(
            db=db,
            user_id=user.id,
            item_id=item_id,
            quantity=payload.quantity
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return cart_service.get_cart(db, user.id)


@router.delete("/items/{item_id}", response_model=CartResponse)
def remove_item(
    item_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_user)
):
    try:
        cart_service.remove_item(
            db=db,
            user_id=user.id,
            item_id=item_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return cart_service.get_cart(db, user.id)


@router.post("/checkout", status_code=201)
def checkout(
    payload: CheckoutRequest,
    db: Session = Depends(get_db),
    user=Depends(require_user)
):
    return cart_service.checkout(
        db=db,
        user_id=user.id,
        shipping_address=payload.shipping_address
    )
