from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MessageCreate(BaseModel):
    """Schema for creating a message"""
    sender_uid: str
    receiver_uid: str
    message: str


class MessageResponse(BaseModel):
    """Schema for message response"""
    uid: str
    sender_uid: str
    receiver_uid: str
    message: str
    is_read: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Schema for conversation response"""
    user_uid: str
    user_name: str
    profile_picture: Optional[str] = None
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    unread_count: int
    is_online: bool = False

    class Config:
        from_attributes = True
