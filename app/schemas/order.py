from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OrderCreate(BaseModel):
    farm_product_uid: str
    quantity: int = Field(..., gt=0)
    payment_method: str = Field(..., pattern="^(Cash on Delivery|Meet Up \/ Cash on Pick-up)$")
    buyer_address: str = Field(..., min_length=2)

class OrderStatusUpdate(BaseModel):
    order_status: str = Field(..., pattern="^(Pending|Confirmed|Cancelled|Delivered)$")


class OrderResponse(BaseModel):
    uid: str
    buyer_uid: str  # Required field
    buyer_name: str
    buyer_contact: str
    seller_uid: str  # Required field
    seller_name: str
    seller_contact: str
    farm_product_uid: str
    farm_product_name: str
    quantity: int
    total_price: float
    order_status: str
    payment_method: str
    is_reviewed: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
