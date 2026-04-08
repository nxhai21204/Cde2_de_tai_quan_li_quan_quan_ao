# app/services/payment_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from decimal import Decimal
from app.models.payment import Payment
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.inventories import Inventory
from app.models.payment_history import PaymentHistory
from app.models.inventory_log import InventoryLog

class PaymentService:
    def create_payment(self, db: Session, order_id: int, method: str):
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(404, "Order not found")
        if order.payment_status == "paid":
            raise HTTPException(400, "Order already paid")

        payment = Payment(order_id=order.id, method=method, amount=order.total_amount, status="pending")
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    def confirm_payment(self, db: Session, payment_id: int, transaction_id: str):
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(404, "Payment not found")
        if payment.status == "success":
            return payment

        order = db.query(Order).filter(Order.id == payment.order_id).with_for_update().first()
        if not order:
            raise HTTPException(404, "Order not found")

        # Deduct inventory for each order_item
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for oi in order_items:
            inv = db.query(Inventory).filter(Inventory.product_variant_id == oi.product_variant_id).with_for_update().first()
            if not inv or inv.quantity < oi.quantity:
                raise HTTPException(400, f"Not enough stock for variant {oi.product_variant_id}")
            inv.quantity -= oi.quantity
            # log
            log = InventoryLog(product_variant_id=oi.product_variant_id, order_id=order.id, qty=oi.quantity, action="deduct", note=f"Payment {payment_id}")
            db.add(log)

        payment.status = "success"
        payment.transaction_id = transaction_id
        order.payment_status = "paid"
        order.status = "paid"
        # payment history
        ph = PaymentHistory(payment_id=payment.id, old_status="pending", new_status="success", note="Payment confirmed")
        db.add(ph)

        db.commit()
        db.refresh(payment)
        return payment

    def refund_payment(self, db: Session, payment_id: int):
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(404, "Payment not found")
        if payment.status != "success":
            raise HTTPException(400, "Only successful payments can be refunded")

        order = db.query(Order).filter(Order.id == payment.order_id).first()
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for oi in order_items:
            inv = db.query(Inventory).filter(Inventory.product_variant_id == oi.product_variant_id).first()
            if inv:
                inv.quantity += oi.quantity
                log = InventoryLog(product_variant_id=oi.product_variant_id, order_id=order.id, qty=oi.quantity, action="restore", note=f"Refund {payment_id}")
                db.add(log)

        payment.status = "refunded"
        order.payment_status = "refunded"
        order.status = "refunded"
        ph = PaymentHistory(payment_id=payment.id, old_status="success", new_status="refunded", note="Refunded by admin")
        db.add(ph)
        db.commit()
        db.refresh(payment)
        return payment

payment_service = PaymentService()
