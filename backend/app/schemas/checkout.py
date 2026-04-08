from pydantic import BaseModel, Field


class CheckoutRequest(BaseModel):
    shipping_address: str = Field(
        ...,
        min_length=5,
        description="Địa chỉ nhận hàng"
    )
