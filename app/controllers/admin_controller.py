from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from neomodel import db
from neo4j import exceptions as neo4j_exceptions
import time
import json
from ..models import User, Buyer, Seller, FarmProduct, Order
from ..schemas import (
    AdminUpdate, AdminResponse, UserManagement, 
    ProductManagement, OrderManagement, DashboardStats
)
from ..utils.dependencies import _retry_get_or_none


class AdminController:
    """Controller for Admin CRUD operations using unified User model"""

    @staticmethod
    def get_admin(admin_uid: str) -> AdminResponse:
        """Get admin by UID using User model"""
        user = _retry_get_or_none(User, uid=admin_uid)
        if not user or user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        return AdminController._to_response(user)
    
    @staticmethod
    def get_all_admins() -> List[AdminResponse]:
        """Get all admins using User model"""
        query = """
        MATCH (u:User {role: 'admin'})
        RETURN u.uid AS uid, u.phone_number AS phone_number, u.full_name AS full_name,
               u.role AS role, u.location AS location, u.created_at AS created_at,
               u.updated_at AS updated_at
        ORDER BY u.created_at DESC
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
            admins.append(AdminResponse(
                uid=row[0],
                phone_number=row[1],
                full_name=row[2],
                role=row[3],
                location=row[4],
                created_at=row[5],
                updated_at=row[6]
            ))

        return admins
    
    @staticmethod
    def update_admin(admin_uid: str, admin_data: AdminUpdate) -> AdminResponse:
        """Update admin information using User model"""
        user = _retry_get_or_none(User, uid=admin_uid)
        if not user or user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )

        # Update fields if provided
        if admin_data.full_name is not None:
            user.full_name = admin_data.full_name

        if admin_data.location is not None:
            user.location = admin_data.location

        user.save()
        return AdminController._to_response(user)

    @staticmethod
    def delete_admin(admin_uid: str) -> dict:
        """Delete an admin using User model"""
        user = _retry_get_or_none(User, uid=admin_uid)
        if not user or user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )

        user.delete()
        return {"message": "Admin deleted successfully"}
    
    @staticmethod
    def manage_user(admin_uid: str, user_mgmt: UserManagement, ip_address: str = None) -> dict:
        """Manage users (approve, block, unblock, ban) using User model"""
        admin = _retry_get_or_none(User, uid=admin_uid)
        if not admin or admin.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )

        # Get user based on type
        if user_mgmt.user_type == "buyer":
            user = _retry_get_or_none(User, uid=user_mgmt.user_uid, role="buyer")
        elif user_mgmt.user_type == "seller":
            user = _retry_get_or_none(User, uid=user_mgmt.user_uid, role="seller")
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
            action_result = f"User {user_mgmt.user_uid} approved"
        elif user_mgmt.action == "block":
            action_result = f"User {user_mgmt.user_uid} blocked"
        elif user_mgmt.action == "unblock":
            action_result = f"User {user_mgmt.user_uid} unblocked"
        elif user_mgmt.action == "ban":
            action_result = f"User {user_mgmt.user_uid} banned"

        return {"message": action_result}

    @staticmethod
    def manage_product(admin_uid: str, product_mgmt: ProductManagement, ip_address: str = None) -> dict:
        """Manage products (approve, remove, flag) using User model"""
        admin = _retry_get_or_none(User, uid=admin_uid)
        if not admin or admin.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )

        product = _retry_get_or_none(FarmProduct, uid=product_mgmt.product_uid)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Perform action
        if product_mgmt.action == "approve":
            action_result = f"Product {product_mgmt.product_uid} approved"
        elif product_mgmt.action == "remove":
            product.delete()
            action_result = f"Product {product_mgmt.product_uid} removed"
        elif product_mgmt.action == "flag":
            action_result = f"Product {product_mgmt.product_uid} flagged"

        return {"message": action_result}
    
    @staticmethod
    def get_dashboard_stats() -> DashboardStats:
        """Get dashboard statistics using User model"""
        # Get user counts using Cypher queries
        buyer_query = "MATCH (u:User {role: 'buyer'}) RETURN count(u) as count"
        seller_query = "MATCH (u:User {role: 'seller'}) RETURN count(u) as count"
        admin_query = "MATCH (u:User {role: 'admin'}) RETURN count(u) as count"

        try:
            buyer_results, _ = db.cypher_query(buyer_query)
            buyer_count = buyer_results[0][0] if buyer_results else 0
        except:
            buyer_count = 0

        try:
            seller_results, _ = db.cypher_query(seller_query)
            seller_count = seller_results[0][0] if seller_results else 0
        except:
            seller_count = 0

        try:
            admin_results, _ = db.cypher_query(admin_query)
            admin_count = admin_results[0][0] if admin_results else 0
        except:
            admin_count = 0

        product_count = len(FarmProduct.nodes.all())
        order_count = len(Order.nodes.all())

        # Get recent registrations (last 7 days)
        recent_query = """
        MATCH (u:User)
        WHERE u.created_at >= datetime() - duration({days: 7})
        RETURN count(u) as recent_users
        """

        try:
            results, _ = db.cypher_query(recent_query)
            recent_registrations = results[0][0] if results else 0
        except:
            recent_registrations = 0

        # Get top sellers and popular products (simplified)
        top_sellers = []
        popular_products = []
        daily_sales = []

        return DashboardStats(
            total_users=buyer_count + seller_count + admin_count,
            total_buyers=buyer_count,
            total_sellers=seller_count,
            total_products=product_count,
            total_orders=order_count,
            pending_approvals=0,
            active_disputes=0,
            recent_registrations=recent_registrations,
            top_sellers=top_sellers,
            popular_products=popular_products,
            daily_sales=daily_sales
        )
    
    @staticmethod
    def _to_response(user: User) -> AdminResponse:
        """Convert User model to AdminResponse schema"""
        return AdminResponse(
            uid=user.uid,
            phone_number=user.phone_number,
            full_name=user.full_name,
            role=user.role,
            location=user.location,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
