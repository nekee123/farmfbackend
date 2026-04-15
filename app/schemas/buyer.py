from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class BuyerBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., min_length=11, max_length=11, pattern="^09[0-9]{9}$")
    location: Optional[str] = None


class BuyerCreate(BuyerBase):
    password: str = Field(..., min_length=6, max_length=72)
    confirm_password: str = Field(..., min_length=6, max_length=72)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class BuyerUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, min_length=11, max_length=11, pattern="^09[0-9]{9}$")
    location: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6, max_length=72)
    profile_picture: Optional[str] = Field(None, description="URL or base64 encoded profile picture")


class BuyerResponse(BuyerBase):
    uid: str
    created_at: datetime
    updated_at: datetime
    profile_picture: Optional[str] = None
    
    class Config:
        from_attributes = True


class BuyerLogin(BaseModel):
    phone_number: str = Field(..., min_length=11, max_length=11, pattern="^09[0-9]{9}$")
    password: str
