from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AdminRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    MODERATOR = "moderator"
    SUPPORT = "support"


class AdminBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    full_name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default=AdminRole.MODERATOR.value)
    is_active: bool = Field(default=True)
    permissions: Optional[List[str]] = Field(default_factory=list)


class AdminCreate(AdminBase):
    password: str = Field(..., min_length=8, max_length=72)
    confirm_password: str = Field(..., min_length=8, max_length=72)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('role')
    def validate_role(cls, v):
        if v not in [role.value for role in AdminRole]:
            raise ValueError(f'Role must be one of: {[role.value for role in AdminRole]}')
        return v


class AdminLogin(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class AdminUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[str] = Field(None)
    is_active: Optional[bool] = None
    permissions: Optional[List[str]] = None
    password: Optional[str] = Field(None, min_length=8, max_length=72)
    
    @validator('role')
    def validate_role(cls, v):
        if v is not None and v not in [role.value for role in AdminRole]:
            raise ValueError(f'Role must be one of: {[role.value for role in AdminRole]}')
        return v


class AdminResponse(AdminBase):
    uid: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserManagement(BaseModel):
    """Schema for user management actions"""
    user_uid: str = Field(..., description="UID of the user to manage")
    user_type: str = Field(..., pattern=r'^(buyer|seller)$')
    action: str = Field(..., pattern=r'^(approve|block|unblock|ban)$')
    reason: Optional[str] = Field(None, max_length=500)


class ProductManagement(BaseModel):
    """Schema for product management actions"""
    product_uid: str = Field(..., description="UID of the product to manage")
    action: str = Field(..., pattern=r'^(approve|remove|flag)$')
    reason: Optional[str] = Field(None, max_length=500)


class OrderManagement(BaseModel):
    """Schema for order management actions"""
    order_uid: str = Field(..., description="UID of the order to manage")
    action: str = Field(..., pattern=r'^(resolve_dispute|cancel|refund|mark_delivered)$')
    resolution: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = Field(None, max_length=500)


class SystemSettings(BaseModel):
    """Schema for system settings"""
    platform_name: Optional[str] = Field(None, max_length=100)
    allowed_categories: Optional[List[str]] = None
    max_products_per_seller: Optional[int] = Field(None, ge=1)
    require_seller_verification: Optional[bool] = None
    platform_policies: Optional[dict] = None


class AdminActivityResponse(BaseModel):
    """Schema for admin activity logs"""
    uid: str
    admin_uid: str
    action: str
    target_type: str
    target_uid: str
    description: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    """Schema for dashboard statistics"""
    total_users: int
    total_buyers: int
    total_sellers: int
    total_products: int
    total_orders: int
    pending_approvals: int
    active_disputes: int
    recent_registrations: int
    top_sellers: List[dict]
    popular_products: List[dict]
    daily_sales: List[dict]
