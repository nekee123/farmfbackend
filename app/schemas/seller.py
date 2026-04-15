from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class SellerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., min_length=11, max_length=11, pattern="^09[0-9]{9}$")
    location: Optional[str] = None


class SellerCreate(SellerBase):
    password: str = Field(..., min_length=6, max_length=72)
    confirm_password: str = Field(..., min_length=6, max_length=72)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class SellerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, min_length=11, max_length=11, pattern="^09[0-9]{9}$")
    location: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, max_length=72)
    profile_picture: Optional[str] = Field(None, description="URL or base64 encoded profile picture")


class SellerResponse(SellerBase):
    uid: str
    created_at: datetime
    updated_at: datetime
    profile_picture: Optional[str] = None
    
    class Config:
        from_attributes = True


class SellerLogin(BaseModel):
    phone_number: str = Field(..., min_length=11, max_length=11, pattern="^09[0-9]{9}$")
    password: str
