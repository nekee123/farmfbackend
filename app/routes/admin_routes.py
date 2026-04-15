from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from ..controllers import AdminController
from ..schemas import (
    AdminCreate, AdminLogin, AdminUpdate, AdminResponse, 
    UserManagement, ProductManagement, OrderManagement, DashboardStats
)
from ..utils.dependencies import get_current_admin, get_admin_from_token
from ..utils.security import create_access_token
from datetime import timedelta

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.post("/register", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
def register_admin(admin_data: AdminCreate):
    """Register a new admin (super admin only)"""
    return AdminController.create_admin(admin_data)


@router.post("/login")
def login_admin(login_data: AdminLogin):
    """Admin login"""
    admin = AdminController.login_admin(login_data.username, login_data.password)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": admin.uid, "username": admin.username, "role": admin.role},
        expires_delta=timedelta(hours=24)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "admin": admin
    }


@router.get("/me", response_model=AdminResponse)
def get_current_admin_info(current_admin = Depends(get_current_admin)):
    """Get current admin information"""
    return current_admin


@router.get("/", response_model=List[AdminResponse])
def get_all_admins(current_admin = Depends(get_current_admin)):
    """Get all admins (super admin only)"""
    # Check if current admin is super admin
    if current_admin.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return AdminController.get_all_admins()


@router.get("/{admin_uid}", response_model=AdminResponse)
def get_admin(admin_uid: str, current_admin = Depends(get_current_admin)):
    """Get admin by UID"""
    # Check if current admin is super admin or requesting their own info
    if current_admin.role != "super_admin" and current_admin.uid != admin_uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return AdminController.get_admin(admin_uid)


@router.put("/{admin_uid}", response_model=AdminResponse)
def update_admin(admin_uid: str, admin_data: AdminUpdate, 
                current_admin = Depends(get_current_admin)):
    """Update admin information"""
    # Check if current admin is super admin or updating their own info
    if current_admin.role != "super_admin" and current_admin.uid != admin_uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return AdminController.update_admin(admin_uid, admin_data)


@router.delete("/{admin_uid}")
def delete_admin(admin_uid: str, current_admin = Depends(get_current_admin)):
    """Delete admin (super admin only)"""
    # Check if current admin is super admin
    if current_admin.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return AdminController.delete_admin(admin_uid)


# User Management Routes
@router.post("/users/manage")
def manage_user(user_mgmt: UserManagement, request: Request, 
               current_admin = Depends(get_current_admin)):
    """Manage users (approve, block, unblock, ban)"""
    ip_address = request.client.host
    return AdminController.manage_user(
        current_admin.uid, user_mgmt, ip_address
    )


# Product Management Routes
@router.post("/products/manage")
def manage_product(product_mgmt: ProductManagement, request: Request,
                 current_admin = Depends(get_current_admin)):
    """Manage products (approve, remove, flag)"""
    ip_address = request.client.host
    return AdminController.manage_product(
        current_admin.uid, product_mgmt, ip_address
    )


# Order Management Routes
@router.post("/orders/manage")
def manage_order(order_mgmt: OrderManagement, request: Request,
                current_admin = Depends(get_current_admin)):
    """Manage orders (resolve disputes, cancel, refund, mark delivered)"""
    ip_address = request.client.host
    # Implement order management logic
    return {"message": "Order management endpoint (to be implemented)"}


# Dashboard and Reports
@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(current_admin = Depends(get_current_admin)):
    """Get dashboard statistics"""
    return AdminController.get_dashboard_stats()


@router.get("/activity/logs")
def get_activity_logs(current_admin = Depends(get_current_admin)):
    """Get admin activity logs"""
    # Implement activity logs retrieval
    return {"message": "Activity logs endpoint (to be implemented)"}


# System Control Routes
@router.get("/system/settings")
def get_system_settings(current_admin = Depends(get_current_admin)):
    """Get system settings"""
    # Implement system settings retrieval
    return {"message": "System settings endpoint (to be implemented)"}


@router.put("/system/settings")
def update_system_settings(request: Request, 
                       current_admin = Depends(get_current_admin)):
    """Update system settings"""
    # Implement system settings update
    return {"message": "System settings update endpoint (to be implemented)"}
