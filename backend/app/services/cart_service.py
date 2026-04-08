from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from datetime import datetime
from app.models.order import PaymentStatus, OrderStatus
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product_variant import ProductVariant
# cart_service.py
from app.models.order import Order
from app.models.order_item import OrderItem



class CartService:

    # =========================
    # GET OR CREATE CART
    # =========================
    def get_or_create_cart(self, db: Session, user_id: int) -> Cart:
        cart = (
            db.query(Cart)
            .options(joinedload(Cart.items).joinedload(CartItem.variant))
            .filter(Cart.user_id == user_id)
            .first()
        )
        if not cart:
            cart = Cart(user_id=user_id)
            db.add(cart)
            db.commit()
            db.refresh(cart)
        return cart

    # =========================
    # ADD ITEM
    # =========================
    def add_item(self, db: Session, user_id: int, product_variant_id: int, quantity: int):
        if quantity <= 0:
            raise HTTPException(400, "Số lượng phải lớn hơn 0")

        cart = self.get_or_create_cart(db, user_id)

        variant = (
            db.query(ProductVariant)
            .filter(ProductVariant.id == product_variant_id)
            .with_for_update()
            .first()
        )

        if not variant:
            raise HTTPException(404, "Không tồn tại mặt hàng này")

        if variant.stock < quantity:
            raise HTTPException(400, "Sản phẩm không đủ số lượng")

        item = (
            db.query(CartItem)
            .filter(
                CartItem.cart_id == cart.id,
                CartItem.product_variant_id == product_variant_id
            )
            .first()
        )

        if item:
            if variant.stock < item.quantity + quantity:
                raise HTTPException(400, "Sản phẩm không đủ số lượng")
            item.quantity += quantity
        else:
            item = CartItem(
                cart_id=cart.id,
                product_variant_id=product_variant_id,
                quantity=quantity,
                price=variant.price
            )
            db.add(item)

        db.commit()
        return self.get_cart(db, user_id)

    # =========================
    # GET CART
    # =========================
    def get_cart(self, db: Session, user_id: int):
        cart = self.get_or_create_cart(db, user_id)

        items = []
        total = 0.0

        for item in cart.items:
            if not item.variant or not item.variant.product:
                continue  # phòng tránh dữ liệu lỗi

            price = float(item.variant.price)
            subtotal = price * item.quantity
            total += subtotal

            items.append({
                "id": item.id,
                "product_variant_id": item.product_variant_id,
                "product_name": item.variant.product.name,
                "size": item.variant.size,
                "color": item.variant.color,
                "quantity": item.quantity,
                "price": price,
                "subtotal": subtotal
            })

        return {
            "id": cart.id,
            "items": items,
            "total": total
        }

    # =========================
    # UPDATE ITEM
    # =========================
    def update_item_quantity(self, db: Session, user_id: int, item_id: int, payload):
        cart = self.get_or_create_cart(db, user_id)

        item = (
            db.query(CartItem)
            .filter(CartItem.id == item_id, CartItem.cart_id == cart.id)
            .first()
        )
        if not item:
            raise HTTPException(404, "Item không tồn tại")

        if item.variant.stock < payload.quantity:
            raise HTTPException(400, "Sản phẩm không đủ số lượng")

        item.quantity = payload.quantity
        db.commit()

        return self.get_cart(db, user_id)

    # =========================
    # REMOVE ITEM
    # =========================
    def remove_item(self, db: Session, user_id: int, item_id: int):
        # Lấy giỏ hàng của user
        cart = self.get_or_create_cart(db, user_id)

        # Tìm item cần xóa trong giỏ hàng
        item = db.query(CartItem).filter(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id
        ).first()

        if not item:
            raise HTTPException(404, "Sản phẩm không tồn tại trong giỏ hàng")

        # Xóa item
        db.delete(item)
        db.commit()

        # Trả về giỏ hàng mới sau khi xóa
        return self.get_cart(db, user_id)

    # =========================
    # CHECKOUT
    # =========================
    def checkout(self, db: Session, user_id: int, shipping_address: str):
        cart = self.get_or_create_cart(db, user_id)

        if not cart.items:
            raise HTTPException(400, "Giỏ hàng trống")

        total = sum(item.variant.price * item.quantity for item in cart.items)

        # Tạo order
        order = Order(
            user_id=user_id,
            total_amount=total,
            payment_method="COD",
            status=OrderStatus.pending.value,
            payment_status=PaymentStatus.unpaid.value,
            created_at=datetime.utcnow(),
            # Nếu trong model bạn có trường shipping_address, thì thêm:
            shipping_address=shipping_address
        )
        db.add(order)
        db.flush()

        for item in cart.items:
            db.add(OrderItem(
                order_id=order.id,
                product_variant_id=item.product_variant_id,
                quantity=item.quantity,
                price=item.variant.price
            ))
            item.variant.stock -= item.quantity

        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        db.delete(cart)

        db.commit()
        db.refresh(order)

        return {
            "order_id": order.id,
            "total_amount": total,
            "payment_status": order.payment_status,
            "qr_code": f"/static/qrcode/order_{order.id}.png"
        }

cart_service = CartService()
