from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ProductInfo(BaseModel):
    """Product information for cart items"""
    uid: str
    name: str
    type: str
    price: float
    description: str = ""
    image: str = ""
    payment_methods: str = "CASH_ON_DELIVERY,MEET_UP_CASH_ON_PICKUP"
    
    class Config:
        from_attributes = True


class CartItemBase(BaseModel):
    buyer_uid: str = Field(..., description="Buyer UID")
    product_uid: str = Field(..., description="Product UID")
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")


class CartItemCreate(CartItemBase):
    price_at_time: float = Field(..., gt=0, description="Price at time of adding to cart")


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0, description="New quantity")


class CartItemResponse(BaseModel):
    uid: str
    product_uid: str
    quantity: int
    price_at_time: float
    created_at: datetime
    product: Optional[ProductInfo] = None  # Include product details
    
    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    uid: str
    buyer_uid: str
    items: List[CartItemResponse]
    total_amount: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CartSummary(BaseModel):
    total_items: int
    total_amount: float
    items_count: int
