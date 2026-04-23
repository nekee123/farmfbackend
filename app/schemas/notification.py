from pydantic import BaseModel
from datetime import datetime


class NotificationCreate(BaseModel):
    """Schema for creating a notification"""
    recipient_uid: str
    sender_name: str
    product_name: str
    type: str  # "order_placed", "order_confirmed", "order_rejected"


class NotificationResponse(BaseModel):
    """Schema for notification response"""
    uid: str
    recipient_uid: str
    sender_name: str
    product_name: str
    type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
