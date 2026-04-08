# app/routers/payments_router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.payment_service import payment_service
from app.schemas.payment import PaymentCreate
from app.core.security import require_active_user, require_manager

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])

@router.post("/order/{order_id}")
def create_payment(order_id: int, payload: PaymentCreate, db: Session = Depends(get_db), current_user=Depends(require_active_user)):
    # optionally check order.user_id == current_user.id
    return payment_service.create_payment(db, order_id, payload.method)

@router.post("/{payment_id}/confirm")
def confirm_payment(payment_id: int, tx: str = Query(None), db: Session = Depends(get_db)):
    # This endpoint can be called by payment gateway callback
    return payment_service.confirm_payment(db, payment_id, transaction_id=tx)

@router.post("/{payment_id}/refund")
def refund(payment_id: int, db: Session = Depends(get_db), manager=Depends(require_manager)):
    return payment_service.refund_payment(db, payment_id)
