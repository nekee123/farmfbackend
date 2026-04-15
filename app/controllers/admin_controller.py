from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from neomodel import db
from neo4j import exceptions as neo4j_exceptions
import time
import json
from ..models import Admin, AdminActivity, Buyer, Seller, FarmProduct, Order
from ..schemas import (
    AdminCreate, AdminUpdate, AdminResponse, UserManagement, 
    ProductManagement, OrderManagement, DashboardStats, AdminActivityResponse
)
from ..utils.security import get_password_hash, verify_password


class AdminController:
    """Controller for Admin CRUD operations"""
    
    @staticmethod
    def create_admin(admin_data: AdminCreate) -> AdminResponse:
        """Create a new admin"""
        # Check if username already exists
        existing_admin = Admin.nodes.get_or_none(username=admin_data.username)
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check if email already exists
        existing_email = Admin.nodes.get_or_none(email=admin_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Create new admin
        admin = Admin(
            username=admin_data.username,
            email=admin_data.email,
            full_name=admin_data.full_name,
            role=admin_data.role,
            is_active=admin_data.is_active,
            permissions=json.dumps(admin_data.permissions or []),
            password_hash=get_password_hash(admin_data.password)
        ).save()
        
        return AdminController._to_response(admin)
    
    @staticmethod
    def login_admin(username: str, password: str) -> AdminResponse:
        """Admin login"""
        attempts = 3
        backoff = 0.5
        admin = None
        last_exc = None
        
        for attempt in range(attempts):
            try:
                admin = Admin.nodes.get_or_none(username=username)
                last_exc = None
                break
            except neo4j_exceptions.ServiceUnavailable as e:
                last_exc = e
                time.sleep(backoff * (attempt + 1))
        
        if last_exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database unavailable, please try again later"
            ) from last_exc
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        if not verify_password(password, admin.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Update last login
        admin.update_last_login()
        
        return AdminController._to_response(admin)
    
    @staticmethod
    def get_admin(admin_uid: str) -> AdminResponse:
        """Get admin by UID"""
        admin = Admin.nodes.get_or_none(uid=admin_uid)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        return AdminController._to_response(admin)
    
    @staticmethod
    def get_all_admins() -> List[AdminResponse]:
        """Get all admins"""
        query = """
        MATCH (a:Admin)
        RETURN a.uid AS uid, a.username AS username, a.email AS email,
               a.full_name AS full_name, a.role AS role, a.is_active AS is_active,
               a.permissions AS permissions, a.created_at AS created_at,
               a.updated_at AS updated_at, a.last_login AS last_login
        ORDER BY a.created_at DESC
        """
        
        attempts = 3
        backoff = 0.5
        last_exc = None
        
        for attempt in range(attempts):
            try:
                results, meta = db.cypher_query(query)
                last_exc = None
                break
            except neo4j_exceptions.ServiceUnavailable as e:
                last_exc = e
                time.sleep(backoff * (attempt + 1))
        
        if last_exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database unavailable, please try again later"
            ) from last_exc
        
        admins = []
        for row in results:
            admins.append({
                "uid": row[0],
                "username": row[1],
                "email": row[2],
                "full_name": row[3],
                "role": row[4],
                "is_active": row[5],
                "permissions": json.loads(row[6]) if row[6] else [],
                "created_at": row[7],
                "updated_at": row[8],
                "last_login": row[9]
            })
        
        return admins
    
    @staticmethod
    def update_admin(admin_uid: str, admin_data: AdminUpdate) -> AdminResponse:
        """Update admin information"""
        admin = Admin.nodes.get_or_none(uid=admin_uid)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        
        # Update fields if provided
        if admin_data.username is not None:
            # Check if username already exists
            existing = Admin.nodes.get_or_none(username=admin_data.username)
            if existing and existing.uid != admin_uid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
            admin.username = admin_data.username
        
        if admin_data.email is not None:
            # Check if email already exists
            existing = Admin.nodes.get_or_none(email=admin_data.email)
            if existing and existing.uid != admin_uid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
            admin.email = admin_data.email
        
        if admin_data.full_name is not None:
            admin.full_name = admin_data.full_name
        
        if admin_data.role is not None:
            admin.role = admin_data.role
        
        if admin_data.is_active is not None:
            admin.is_active = admin_data.is_active
        
        if admin_data.permissions is not None:
            admin.permissions = json.dumps(admin_data.permissions)
        
        if admin_data.password is not None:
            admin.password_hash = get_password_hash(admin_data.password)
        
        admin.update_timestamp()
        return AdminController._to_response(admin)
    
    @staticmethod
    def delete_admin(admin_uid: str) -> dict:
        """Delete an admin"""
        admin = Admin.nodes.get_or_none(uid=admin_uid)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        
        admin.delete()
        return {"message": "Admin deleted successfully"}
    
    @staticmethod
    def manage_user(admin_uid: str, user_mgmt: UserManagement, ip_address: str = None) -> dict:
        """Manage users (approve, block, unblock, ban)"""
        admin = Admin.nodes.get_or_none(uid=admin_uid)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        
        # Check permissions
        if not admin.has_permission("manage_users"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Get user based on type
        if user_mgmt.user_type == "buyer":
            user = Buyer.nodes.get_or_none(uid=user_mgmt.user_uid)
        elif user_mgmt.user_type == "seller":
            user = Seller.nodes.get_or_none(uid=user_mgmt.user_uid)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user type"
            )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Perform action
        action_result = ""
        if user_mgmt.action == "approve":
            # Add approval logic here
            action_result = f"User {user_mgmt.user_uid} approved"
        elif user_mgmt.action == "block":
            # Add blocking logic here
            action_result = f"User {user_mgmt.user_uid} blocked"
        elif user_mgmt.action == "unblock":
            # Add unblocking logic here
            action_result = f"User {user_mgmt.user_uid} unblocked"
        elif user_mgmt.action == "ban":
            # Add banning logic here
            action_result = f"User {user_mgmt.user_uid} banned"
        
        # Log activity
        AdminController._log_activity(
            admin_uid, user_mgmt.action, "user", user_mgmt.user_uid,
            f"{action_result}: {user_mgmt.reason or 'No reason provided'}", ip_address
        )
        
        return {"message": action_result}
    
    @staticmethod
    def manage_product(admin_uid: str, product_mgmt: ProductManagement, ip_address: str = None) -> dict:
        """Manage products (approve, remove, flag)"""
        admin = Admin.nodes.get_or_none(uid=admin_uid)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        
        # Check permissions
        if not admin.has_permission("manage_products"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        product = FarmProduct.nodes.get_or_none(uid=product_mgmt.product_uid)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Perform action
        if product_mgmt.action == "approve":
            # Add approval logic here
            action_result = f"Product {product_mgmt.product_uid} approved"
        elif product_mgmt.action == "remove":
            product.delete()
            action_result = f"Product {product_mgmt.product_uid} removed"
        elif product_mgmt.action == "flag":
            # Add flagging logic here
            action_result = f"Product {product_mgmt.product_uid} flagged"
        
        # Log activity
        AdminController._log_activity(
            admin_uid, product_mgmt.action, "product", product_mgmt.product_uid,
            f"{action_result}: {product_mgmt.reason or 'No reason provided'}", ip_address
        )
        
        return {"message": action_result}
    
    @staticmethod
    def get_dashboard_stats() -> DashboardStats:
        """Get dashboard statistics"""
        # Get user counts
        buyer_count = len(Buyer.nodes.all())
        seller_count = len(Seller.nodes.all())
        product_count = len(FarmProduct.nodes.all())
        order_count = len(Order.nodes.all())
        
        # Get recent registrations (last 7 days)
        recent_query = """
        MATCH (u:Buyer)
        WHERE u.created_at >= datetime() - duration({days: 7})
        RETURN count(u) as recent_buyers
        UNION ALL
        MATCH (u:Seller)
        WHERE u.created_at >= datetime() - duration({days: 7})
        RETURN count(u) as recent_sellers
        """
        
        try:
            results, _ = db.cypher_query(recent_query)
            recent_registrations = sum(row[0] for row in results)
        except:
            recent_registrations = 0
        
        # Get top sellers and popular products (simplified)
        top_sellers = []
        popular_products = []
        daily_sales = []
        
        return DashboardStats(
            total_users=buyer_count + seller_count,
            total_buyers=buyer_count,
            total_sellers=seller_count,
            total_products=product_count,
            total_orders=order_count,
            pending_approvals=0,  # Implement logic
            active_disputes=0,    # Implement logic
            recent_registrations=recent_registrations,
            top_sellers=top_sellers,
            popular_products=popular_products,
            daily_sales=daily_sales
        )
    
    @staticmethod
    def _to_response(admin: Admin) -> AdminResponse:
        """Convert Admin model to response schema"""
        return AdminResponse(
            uid=admin.uid,
            username=admin.username,
            email=admin.email,
            full_name=admin.full_name,
            role=admin.role,
            is_active=admin.is_active,
            permissions=admin.get_permissions_list(),
            created_at=admin.created_at,
            updated_at=admin.updated_at,
            last_login=admin.last_login
        )
    
    @staticmethod
    def _log_activity(admin_uid: str, action: str, target_type: str, 
                   target_uid: str, description: str, ip_address: str = None):
        """Log admin activity"""
        activity = AdminActivity(
            admin_uid=admin_uid,
            action=action,
            target_type=target_type,
            target_uid=target_uid,
            description=description,
            ip_address=ip_address
        ).save()
