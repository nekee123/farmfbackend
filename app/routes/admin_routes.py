from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from ..controllers import AdminController
from ..schemas import (
    AdminUpdate, AdminResponse,
    UserManagement, ProductManagement, OrderManagement, DashboardStats
)
from ..utils.dependencies import admin_only
from ..models.user import User

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/me")
def get_current_admin_info(current_user: User = Depends(admin_only)):
    """Get current admin information"""
    return current_user


@router.get("/")
def get_all_admins(current_user: User = Depends(admin_only)):
    """Get all admins (super admin only)"""
    return AdminController.get_all_admins()


@router.get("/users")
def get_all_users(current_user: User = Depends(admin_only)):
    """Get all users for admin management"""
    from neomodel import db
    query = """
    MATCH (u:User)
    RETURN u.uid AS uid, u.phone_number AS phone_number, u.full_name AS full_name,
           u.location AS location, u.role AS role, u.created_at AS created_at
    ORDER BY u.created_at DESC
    """
    results, _ = db.cypher_query(query)
    users = []
    for row in results:
        users.append({
            "uid": row[0],
            "phone_number": row[1],
            "full_name": row[2],
            "location": row[3],
            "role": row[4],
            "created_at": row[5]
        })
    return users


@router.get("/{admin_uid}")
def get_admin(admin_uid: str, current_user: User = Depends(admin_only)):
    """Get admin by UID"""
    return AdminController.get_admin(admin_uid)


@router.put("/{admin_uid}", response_model=AdminResponse)
def update_admin(admin_uid: str, admin_data: AdminUpdate, 
                current_user: User = Depends(admin_only)):
    """Update admin information"""
    return AdminController.update_admin(admin_uid, admin_data)


@router.delete("/{admin_uid}")
def delete_admin(admin_uid: str, current_user: User = Depends(admin_only)):
    """Delete admin (super admin only)"""
    return AdminController.delete_admin(admin_uid)


# User Management Routes
@router.delete("/users/{user_uid}")
def delete_user(user_uid: str, current_user: User = Depends(admin_only)):
    """Delete a user (admin only)"""
    from ..utils.dependencies import _retry_get_or_none
    from ..models import User, FarmProduct, Order
    from neomodel import db

    user = _retry_get_or_none(User, uid=user_uid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent deleting self
    if user.uid == current_user.uid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )

    # Delete related data (products, orders, etc.)
    try:
        # Delete products if seller
        if user.role == "seller":
            products = FarmProduct.nodes.filter(seller__uid=user_uid)
            for product in products:
                product.delete()

        # Delete orders if buyer
        if user.role == "buyer":
            orders = Order.nodes.filter(buyer__uid=user_uid)
            for order in orders:
                order.delete()

        # Delete the user
        user.delete()

        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )


@router.post("/users/manage")
def manage_user(user_mgmt: UserManagement, request: Request,
               current_user: User = Depends(admin_only)):
    """Manage users (approve, block, unblock, ban)"""
    ip_address = request.client.host
    return AdminController.manage_user(
        current_user.uid, user_mgmt, ip_address
    )


# Product Management Routes
@router.post("/products/manage")
def manage_product(product_mgmt: ProductManagement, request: Request,
                 current_user: User = Depends(admin_only)):
    """Manage products (approve, remove, flag)"""
    ip_address = request.client.host
    return AdminController.manage_product(
        current_user.uid, product_mgmt, ip_address
    )


# Order Management Routes
@router.post("/orders/manage")
def manage_order(order_mgmt: OrderManagement, request: Request,
                current_user: User = Depends(admin_only)):
    """Manage orders (resolve disputes, cancel, refund, mark delivered)"""
    ip_address = request.client.host
    # Implement order management logic
    return {"message": "Order management endpoint (to be implemented)"}


# Dashboard and Reports
@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(current_user: User = Depends(admin_only)):
    """Get dashboard statistics"""
    return AdminController.get_dashboard_stats()


@router.get("/stats/users")
def get_users_stats(current_user: User = Depends(admin_only)):
    """Get total users count"""
    stats = AdminController.get_dashboard_stats()
    return {"count": stats.total_users}


@router.get("/stats/products")
def get_products_stats(current_user: User = Depends(admin_only)):
    """Get total products count"""
    stats = AdminController.get_dashboard_stats()
    return {"count": stats.total_products}


@router.get("/stats/orders")
def get_orders_stats(current_user: User = Depends(admin_only)):
    """Get total orders count"""
    stats = AdminController.get_dashboard_stats()
    return {"count": stats.total_orders}


@router.get("/stats/farmers")
def get_farmers_stats(current_user: User = Depends(admin_only)):
    """Get total farmers (sellers) count"""
    stats = AdminController.get_dashboard_stats()
    return {"count": stats.total_sellers}


@router.get("/activity/logs")
def get_activity_logs(current_user: User = Depends(admin_only)):
    """Get admin activity logs"""
    # Implement activity logs retrieval
    return {"message": "Activity logs endpoint (to be implemented)"}


# System Control Routes
@router.get("/system/settings")
def get_system_settings(current_user: User = Depends(admin_only)):
    """Get system settings"""
    # Implement system settings retrieval
    return {"message": "System settings endpoint (to be implemented)"}


@router.put("/system/settings")
def update_system_settings(request: Request, 
                       current_user: User = Depends(admin_only)):
    """Update system settings"""
    # Implement system settings update
    return {"message": "System settings update endpoint (to be implemented)"}
