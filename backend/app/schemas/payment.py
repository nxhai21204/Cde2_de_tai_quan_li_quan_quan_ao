from pydantic import BaseModel

class PaymentCreate(BaseModel):
    method: str  # cod, momo, vnpay, paypal, bank

class PaymentRead(BaseModel):
    id: int
    order_id: int
    method: str
    amount: float
    status: str
    transaction_id: str | None = None
    class Config:
        orm_mode = True
