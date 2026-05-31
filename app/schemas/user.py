from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from ..models.user import UserRole
from typing import List, Optional

class UserBase(BaseModel):
    phone_number: str
    full_name: str
    location: Optional[str] = None
    profile_picture: Optional[str] = None
    
class OTPVerify(BaseModel):
    phone_number: str
    otp: str

class ResendOTP(BaseModel):
    phone_number: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.BUYER
    category: Optional[List[str]] = []

class UserLogin(BaseModel):
    phone_number: str
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    profile_picture: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)


class UserResponse(UserBase):
    uid: str
    role: UserRole
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: str
