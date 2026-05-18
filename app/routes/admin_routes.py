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
    from ..models import User
    from neomodel import db
    import traceback

    print("=== DELETE USER DEBUG START ===")
    print("user_uid:", user_uid)

    user = _retry_get_or_none(User, uid=user_uid)

    print("Fetched user:", user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    print("User UID:", getattr(user, "uid", "NO UID"))
    print("User role:", getattr(user, "role", "NO ROLE"))
    print("Current admin UID:", getattr(current_user, "uid", "NO UID"))

    # Prevent deleting self
    if user.uid == current_user.uid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )

    try:
        # ========================
        # SELLER → delete products
        # ========================
        if user.role == "seller":
            print("Looking for seller products...")

            query = """
            MATCH (p:FarmProduct)-[:SOLD_BY]->(u:User {uid: $uid})
            DETACH DELETE p
            """

            db.cypher_query(query, {"uid": user_uid})

            print("Seller products deleted")

        # ========================
        # BUYER → delete orders
        # ========================
        if user.role == "buyer":
            print("Looking for buyer orders...")

            query = """
            MATCH (o:Order)-[:PLACED_BY]->(u:User {uid: $uid})
            DETACH DELETE o
            """

            db.cypher_query(query, {"uid": user_uid})

            print("Buyer orders deleted")

        # ========================
        # DELETE USER
        # ========================
        print("Deleting user now...")

        query = """
        MATCH (u:User {uid: $uid})
        DETACH DELETE u
        """

        db.cypher_query(query, {"uid": user_uid})

        print("=== DELETE SUCCESS ===")

        return {"message": "User deleted successfully"}

    except Exception as e:
        print("=== DELETE ERROR ===")
        print("Error type:", type(e))
        print("Error:", str(e))
        traceback.print_exc()

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



@router.post("/deals")
def create_deal(data: dict, current_user: User = Depends(admin_only)):
    from datetime import datetime, timedelta
    from neomodel import db
    import uuid

    print("=== CREATE DEAL START ===")
    print("Payload:", data)

    percentage = int(data["percentage"])
    deal_type = data["type"]
    duration_value = int(data["duration_value"])
    duration_unit = data["duration_unit"]

    created_at = datetime.utcnow()

    # compute expiry
    if duration_unit == "hours":
        expires_at = created_at + timedelta(hours=duration_value)
    else:
        expires_at = created_at + timedelta(days=duration_value)

    deal_id = str(uuid.uuid4())

    query = """
    CREATE (d:Deal {
        deal_id: $deal_id,
        percentage: $percentage,
        type: $type,
        duration_value: $duration_value,
        duration_unit: $duration_unit,
        created_at: datetime($created_at),
        expires_at: datetime($expires_at)
    })
    RETURN d
    """

    result, _ = db.cypher_query(query, {
        "deal_id": deal_id,
        "percentage": percentage,
        "type": deal_type,
        "duration_value": duration_value,
        "duration_unit": duration_unit,
        "created_at": created_at.isoformat(),
        "expires_at": expires_at.isoformat()
    })

    print("Deal created:", deal_id)
    print("=== CREATE DEAL END ===")

    return {
        "message": "Deal created successfully",
        "deal_id": deal_id
    }

@router.delete("/deals/{deal_id}")
def delete_deal(deal_id: str, current_user: User = Depends(admin_only)):
    from neomodel import db

    query = """
    MATCH (d:Deal {deal_id: $deal_id})
    DETACH DELETE d
    """

    db.cypher_query(query, {"deal_id": deal_id})

    return {"message": "Deal deleted"}



@router.put("/users/{user_uid}/ban-status")
def update_ban_status(
    user_uid: str,
    data: dict,
    current_user: User = Depends(admin_only)
    ):
    """
    Update user ban status

    Body:
    {
        "is_banned": true
    }
    """

    from ..models import User
    from ..utils.dependencies import _retry_get_or_none

    user = _retry_get_or_none(User, uid=user_uid)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Prevent admin banning self
    if user.uid == current_user.uid:
        raise HTTPException(
            status_code=400,
            detail="You cannot ban yourself"
        )

    # Update value
    user.is_banned = data.get("is_banned", False)

    user.save()

    return {
        "message": "Ban status updated successfully",
        "uid": user.uid,
        "full_name": user.full_name,
        "is_banned": user.is_banned
    }

@router.get("/users/{user_uid}/ban-status")
def get_ban_status(
    user_uid: str,
    current_user: User = Depends(admin_only)
):

    from ..models import User
    from ..utils.dependencies import _retry_get_or_none

    user = _retry_get_or_none(User, uid=user_uid)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "uid": user.uid,
        "full_name": user.full_name,
        "is_banned": user.is_banned
    }