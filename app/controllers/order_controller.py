from typing import List
from fastapi import HTTPException, status
from ..models import Order, FarmProduct, User
from ..utils.dependencies import _retry_get_or_none
from ..schemas import OrderCreate, OrderStatusUpdate, OrderResponse, NotificationCreate
from .notification_controller import NotificationController
from ..database import get_db
from datetime import datetime
from app.controllers.farm_product_controller import FarmProductController
import uuid


class OrderController:
    """Controller for Order CRUD operations using unified User model"""
    
    @staticmethod
    def create_order(order_data: OrderCreate, current_user: User) -> dict:
        """Create a new order for the current authenticated buyer"""
        try:
            # Get product first to validate payment method
            product = _retry_get_or_none(FarmProduct, uid=order_data.farm_product_uid)
            if not product:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

            # Validate payment method against product's available methods
            available_methods = []
            if hasattr(product, 'payment_methods') and product.payment_methods:
                available_methods = [method.strip() for method in product.payment_methods.split(',') if method.strip()]

            # If no payment methods specified, default to both available
            if not available_methods:
                available_methods = ["CASH_ON_DELIVERY", "MEET_UP_CASH_ON_PICKUP"]

            # Convert frontend payment method names to database format
            frontend_to_backend = {
                "Cash on Delivery": "CASH_ON_DELIVERY",
                "Meet Up / Cash on Pick-up": "MEET_UP_CASH_ON_PICKUP"
            }

            backend_payment_method = frontend_to_backend.get(order_data.payment_method, order_data.payment_method)

            if backend_payment_method not in available_methods:
                # Convert available methods to frontend format for error message
                backend_to_frontend = {
                    "CASH_ON_DELIVERY": "Cash on Delivery",
                    "MEET_UP_CASH_ON_PICKUP": "Meet Up / Cash on Pick-up"
                }
                available_labels = [backend_to_frontend.get(method, method) for method in available_methods]
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Payment method '{order_data.payment_method}' is not available for this product. Available methods: {', '.join(available_labels)}"
                )

            if product.quantity < order_data.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient quantity. Available: {product.quantity}"
                )

            # Get seller
            sellers = product.seller.all()
            if not sellers:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product has no seller associated with it")
            seller = sellers[0]

            total_price = product.price * order_data.quantity

            # Create order with buyer_uid and seller_uid
            order = Order(
                buyer_uid=current_user.uid,
                seller_uid=seller.uid,
                quantity=order_data.quantity,
                total_price=total_price,
                payment_method=backend_payment_method,
                buyer_address=order_data.buyer_address,  # 🔥 NEW
                order_status="Pending"
            ).save()

            # Connect relationships
            order.buyer.connect(current_user)
            order.seller.connect(seller)
            order.farm_product.connect(product)

            # Update product quantity
            product.reduce_quantity(order_data.quantity)

            # Create notification for seller
            NotificationController.create_notification(
                NotificationCreate(
                    recipient_uid=seller.uid,
                    sender_name=current_user.full_name,
                    product_name=product.name,
                    type="order_placed"
                )
            )

            return OrderController._to_response(order)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Order creation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Order creation failed: {str(e)}"
            )

    @staticmethod
    def get_order(order_uid: str) -> dict:
        """Get order by UID"""
        order = _retry_get_or_none(Order, uid=order_uid)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return OrderController._to_response(order)

    @staticmethod
    def get_all_orders() -> List[dict]:
        """Get all orders using unified User model"""
        driver = get_db()
        with driver.session() as session:
            query = """
            MATCH (o:Order)
            OPTIONAL MATCH (o)-[:PLACED_BY]->(b:User)
            OPTIONAL MATCH (o)-[:FULFILLED_BY]->(s:User)
            OPTIONAL MATCH (o)-[:CONTAINS]->(p:FarmProduct)
            OPTIONAL MATCH (r:Review {order_uid: o.uid})
            RETURN o.uid as uid, o.buyer_uid as buyer_uid, o.seller_uid as seller_uid,
                   o.quantity as quantity, o.total_price as total_price,
                   o.order_status as order_status, o.payment_method as payment_method,
                   o.created_at as created_at, o.updated_at as updated_at,
                   b.uid as buyer_uid_rel, b.full_name as buyer_name, b.phone_number as buyer_contact,
                   s.uid as seller_uid_rel, s.full_name as seller_name, s.phone_number as seller_contact,
                   p.uid as farm_product_uid, p.name as farm_product_name,
                   count(r) > 0 as is_reviewed
            ORDER BY o.created_at DESC
            """
            
            results = session.run(query)

            orders = []
            for record in results:
                orders.append({
                    "uid": record["uid"],
                    "buyer_uid": record["buyer_uid"] or record["buyer_uid_rel"] or "",
                    "buyer_name": record["buyer_name"] or "",
                    "buyer_contact": record["buyer_contact"] or "N/A",
                    "seller_uid": record["seller_uid"] or record["seller_uid_rel"] or "",
                    "seller_name": record["seller_name"] or "",
                    "seller_contact": record["seller_contact"] or "N/A",
                    "farm_product_uid": record["farm_product_uid"] or "",
                    "farm_product_name": record["farm_product_name"] or "",
                    "quantity": record["quantity"],
                    "total_price": record["total_price"],
                    "order_status": record["order_status"],
                    "payment_method": record["payment_method"],
                    "is_reviewed": bool(record["is_reviewed"]),
                    "created_at": record["created_at"],
                    "updated_at": record["updated_at"]
                })
            
            return orders

    @staticmethod
    def get_buyer_orders(buyer_uid: str) -> List[dict]:
        """Get orders for a specific buyer"""
        driver = get_db()
        with driver.session() as session:
            query = """
            MATCH (b:User {uid: $buyer_uid})-[:PLACED_BY]-(o:Order)
            OPTIONAL MATCH (o)-[:FULFILLED_BY]->(s:User)
            OPTIONAL MATCH (o)-[:CONTAINS]->(p:FarmProduct)
            OPTIONAL MATCH (r:Review {order_uid: o.uid})
            RETURN o.uid as uid, o.buyer_uid as buyer_uid, o.seller_uid as seller_uid,
                   o.quantity as quantity, o.total_price as total_price,
                   o.buyer_address as buyer_address,
                   o.order_status as order_status, o.payment_method as payment_method,
                   o.created_at as created_at, o.updated_at as updated_at,
                   b.uid as buyer_uid_rel, b.full_name as buyer_name, b.phone_number as buyer_contact,
                   s.uid as seller_uid_rel, s.full_name as seller_name, s.phone_number as seller_contact,
                   p.uid as farm_product_uid, p.name as farm_product_name,
                   count(r) > 0 as is_reviewed
            ORDER BY o.created_at DESC
            """

            results = session.run(query, {"buyer_uid": buyer_uid})

            orders = []
            for record in results:
                orders.append({
                    "uid": record["uid"],
                    "buyer_uid": record["buyer_uid"] or record["buyer_uid_rel"] or "",
                    "buyer_name": record["buyer_name"] or "",
                    "buyer_contact": record["buyer_contact"] or "N/A",
                    "seller_uid": record["seller_uid"] or record["seller_uid_rel"] or "",
                    "seller_name": record["seller_name"] or "",
                    "seller_contact": record["seller_contact"] or "N/A",
                    "farm_product_uid": record["farm_product_uid"] or "",
                    "farm_product_name": record["farm_product_name"] or "",
                    "quantity": record["quantity"],
                    "total_price": record["total_price"],
                    "order_status": record["order_status"],
                    "payment_method": record["payment_method"],
                    "buyer_address": record["buyer_address"] or "N/A",
                    "is_reviewed": bool(record["is_reviewed"]),
                    "created_at": record["created_at"],
                    "updated_at": record["updated_at"]
                })

            return orders

    @staticmethod
    def get_seller_orders(seller_uid: str) -> List[dict]:
        """Get orders for a specific seller"""
        driver = get_db()
        with driver.session() as session:
            query = """
            MATCH (s:User {uid: $seller_uid})-[:FULFILLED_BY]-(o:Order)
            OPTIONAL MATCH (o)-[:PLACED_BY]->(b:User)
            OPTIONAL MATCH (o)-[:CONTAINS]->(p:FarmProduct)
            OPTIONAL MATCH (r:Review {order_uid: o.uid})
            RETURN o.uid as uid, o.buyer_uid as buyer_uid, o.seller_uid as seller_uid,
                   o.quantity as quantity, o.total_price as total_price,
                   o.buyer_address as buyer_address,
                   o.order_status as order_status, o.payment_method as payment_method,
                   o.created_at as created_at, o.updated_at as updated_at,
                   b.uid as buyer_uid_rel, b.full_name as buyer_name, b.phone_number as buyer_contact,
                   s.uid as seller_uid_rel, s.full_name as seller_name, s.phone_number as seller_contact,
                   p.uid as farm_product_uid, p.name as farm_product_name,
                   count(r) > 0 as is_reviewed
            ORDER BY o.created_at DESC
            """

            results = session.run(query, {"seller_uid": seller_uid})

            orders = []
            for record in results:
                orders.append({
                    "uid": record["uid"],
                    "buyer_uid": record["buyer_uid"] or record["buyer_uid_rel"] or "",
                    "buyer_name": record["buyer_name"] or "",
                    "buyer_contact": record["buyer_contact"] or "N/A",
                    "seller_uid": record["seller_uid"] or record["seller_uid_rel"] or "",
                    "seller_name": record["seller_name"] or "",
                    "seller_contact": record["seller_contact"] or "N/A",
                    "farm_product_uid": record["farm_product_uid"] or "",
                    "farm_product_name": record["farm_product_name"] or "",
                    "quantity": record["quantity"],
                    "total_price": record["total_price"],
                    "order_status": record["order_status"],
                    "payment_method": record["payment_method"],
                    "buyer_address": record["buyer_address"] or "N/A",
                    "is_reviewed": bool(record["is_reviewed"]),
                    "created_at": record["created_at"],
                    "updated_at": record["updated_at"]
                })

            return orders

    @staticmethod
    def _to_response(order: Order) -> dict:
        """Convert Order model to response dictionary including buyer and seller contacts"""
        buyers = order.buyer.all()
        sellers = order.seller.all()
        products = order.farm_product.all()

        buyer = buyers[0] if buyers else None
        seller = sellers[0] if sellers else None
        product = products[0] if products else None

        # Check if order has been reviewed
        reviewed = False
        if order.uid:
            try:
                driver = get_db()
                with driver.session() as session:
                    review_check = session.run(
                        "MATCH (r:Review {order_uid: $order_uid}) RETURN count(r) as count",
                        {"order_uid": order.uid}
                    )
                    result = review_check.single()
                    reviewed = result["count"] > 0 if result else False
            except Exception:
                reviewed = False

        return {
            "uid": order.uid,
            "buyer_uid": order.buyer_uid if hasattr(order, 'buyer_uid') and order.buyer_uid else (buyer.uid if buyer else ""),
            "buyer_name": buyer.full_name if buyer else "",
            "buyer_contact": buyer.phone_number if buyer else "N/A",
            "seller_uid": order.seller_uid if hasattr(order, 'seller_uid') and order.seller_uid else (seller.uid if seller else ""),
            "seller_name": seller.full_name if seller else "",
            "seller_contact": seller.phone_number if seller else "N/A",
            "farm_product_uid": product.uid if product else "",
            "farm_product_name": product.name if product else "",
            "quantity": order.quantity,
            "total_price": order.total_price,
            "order_status": order.order_status,
            "payment_method": order.payment_method,
            "is_reviewed": reviewed,
            "reviewed": reviewed,
            "created_at": order.created_at,
            "updated_at": order.updated_at
        }

    @staticmethod
    def cancel_order(order_uid: str, buyer_uid: str) -> dict:
        """Cancel an order (buyer can only cancel their own pending orders)"""
        order = _retry_get_or_none(Order, uid=order_uid)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        # Verify order belongs to the buyer
        if order.buyer_uid != buyer_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only cancel your own orders"
            )

        # Verify order is in pending status
        if order.order_status != "Pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel order with status '{order.order_status}'. Only pending orders can be cancelled."
            )

        # Restore product quantity
        products = order.farm_product.all()
        if products:
            product = products[0]
            product.quantity += order.quantity
            product.update_timestamp()

        # Update order status
        order.order_status = "Cancelled"
        order.update_timestamp()

        return {
            "success": True,
            "message": "Order cancelled successfully",
            "order_uid": order.uid,
            "order_status": order.order_status
        }

    @staticmethod
    def confirm_order(order_uid: str, seller_uid: str) -> dict:
        """Confirm an order (seller can only confirm orders they are fulfilling)"""
        order = _retry_get_or_none(Order, uid=order_uid)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        # Verify order belongs to the seller
        if order.seller_uid != seller_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only confirm orders assigned to you"
            )

        # Verify order is in pending status
        if order.order_status != "Pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot confirm order with status '{order.order_status}'. Only pending orders can be confirmed."
            )

        # Update order status
        order.order_status = "Confirmed"
        order.update_timestamp()

        # Create notification for buyer
        buyers = order.buyer.all()
        sellers = order.seller.all()
        if buyers and sellers:
            buyer = buyers[0]
            seller = sellers[0]
            products = order.farm_product.all()
            product_name = products[0].name if products else ""
            NotificationController.create_notification(
                NotificationCreate(
                    recipient_uid=buyer.uid,
                    sender_name=seller.full_name,
                    product_name=product_name,
                    type="order_confirmed"
                )
            )

        return {
            "success": True,
            "message": "Order confirmed successfully",
            "order_uid": order.uid,
            "order_status": order.order_status
        }

    @staticmethod
    def reject_order(order_uid: str, seller_uid: str) -> dict:
        """Reject an order (seller can only reject orders they are fulfilling)"""
        order = _retry_get_or_none(Order, uid=order_uid)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        # Verify order belongs to the seller
        if order.seller_uid != seller_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only reject orders assigned to you"
            )

        # Verify order is in pending status
        if order.order_status != "Pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reject order with status '{order.order_status}'. Only pending orders can be rejected."
            )

        # Restore product quantity
        products = order.farm_product.all()
        if products:
            product = products[0]
            product.quantity += order.quantity
            product.update_timestamp()

        # Update order status
        order.order_status = "Cancelled"
        order.update_timestamp()

        # Create notification for buyer
        buyers = order.buyer.all()
        sellers = order.seller.all()
        if buyers and sellers:
            buyer = buyers[0]
            seller = sellers[0]
            products = order.farm_product.all()
            product_name = products[0].name if products else ""
            NotificationController.create_notification(
                NotificationCreate(
                    recipient_uid=buyer.uid,
                    sender_name=seller.full_name,
                    product_name=product_name,
                    type="order_rejected"
                )
            )

        return {
            "success": True,
            "message": "Order rejected successfully",
            "order_uid": order.uid,
            "order_status": order.order_status
        }

    @staticmethod
    def mark_order_delivered(order_uid: str, seller_uid: str) -> dict:
        """Mark an order as delivered (seller can only mark their own orders as delivered)"""
        order = _retry_get_or_none(Order, uid=order_uid)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        # Verify order belongs to the seller
        if order.seller_uid != seller_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only mark as delivered orders assigned to you"
            )

        # Verify order is in confirmed or processing status
        if order.order_status not in ["Confirmed", "Processing"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot mark order as delivered with status '{order.order_status}'. Only confirmed/processing orders can be marked as delivered."
            )

        # Update order status
        order.order_status = "Delivered"
        order.update_timestamp()

        # Create notification for buyer
        buyers = order.buyer.all()
        sellers = order.seller.all()
        if buyers and sellers:
            buyer = buyers[0]
            seller = sellers[0]
            products = order.farm_product.all()
            product_name = products[0].name if products else ""
            NotificationController.create_notification(
                NotificationCreate(
                    recipient_uid=buyer.uid,
                    sender_name=seller.full_name,
                    product_name=product_name,
                    type="order_delivered"
                )
            )

        return {
            "success": True,
            "message": "Order marked as delivered",
            "order_uid": order.uid,
            "order_status": order.order_status
        }

    @staticmethod
    def update_order_status(order_uid: str, status_data: OrderStatusUpdate) -> dict:
        """Update order status"""
        allowed_statuses = ["Pending", "Confirmed", "Cancelled", "Delivered"]
        if status_data.order_status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order status must be one of: {', '.join(allowed_statuses)}"
            )

        order = _retry_get_or_none(Order, uid=order_uid)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        if order.order_status == "Delivered" and status_data.order_status != "Delivered":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is already delivered and cannot be changed"
            )

        # Handle cancelled orders - restore product quantity
        if order.order_status != "Cancelled" and status_data.order_status == "Cancelled":
            products = order.farm_product.all()
            if products:
                product = products[0]
                product.quantity += order.quantity
                product.update_timestamp()

        order.order_status = status_data.order_status
        order.update_timestamp()

        return {
            "message": "Order status updated successfully",
            "order_uid": order.uid,
            "order_status": order.order_status
        }

    @staticmethod
    def delete_order(order_uid: str, seller_uid: str = None) -> dict:
        """Delete an order (Admin can delete all, Sellers can only delete their own cancelled/rejected orders)"""
        order = _retry_get_or_none(Order, uid=order_uid)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        # If seller_uid is provided (seller is deleting), validate ownership and status
        if seller_uid:
            # Verify order belongs to the seller
            if order.seller_uid != seller_uid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only delete your own orders"
                )

            # Verify order is cancelled or rejected
            if order.order_status not in ["Cancelled", "Cancelled"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot delete order with status '{order.order_status}'. Only cancelled or rejected orders can be deleted."
                )
        else:
            # Admin deleting - restore product quantity if order was pending
            if order.order_status == "Pending":
                products = order.farm_product.all()
                if products:
                    product = products[0]
                    product.quantity += order.quantity
                    product.update_timestamp()

        order.delete()
        return {"message": "Order deleted successfully"}
    

def create_favorite(user_uid: str, product_uid: str):
    driver = get_db()
    with driver.session() as session:
        query = """
        MATCH (u:User {uid: $user_uid})
        MATCH (p:FarmProduct {uid: $product_uid})
        MERGE (u)-[:FAVORITE]->(p)
        RETURN p
        """
        session.run(query, {
            "user_uid": user_uid,
            "product_uid": product_uid
        })


def remove_favorite(user_uid: str, product_uid: str):
    driver = get_db()
    with driver.session() as session:
        query = """
        MATCH (u:User {uid: $user_uid})-[f:FAVORITE]->(p:FarmProduct {uid: $product_uid})
        DELETE f
        """
        session.run(query, {
            "user_uid": user_uid,
            "product_uid": product_uid
        })

def get_favorite_products(user_uid: str):
    driver = get_db()
    with driver.session() as session:
        query = """
        MATCH (u:User {uid: $user_uid})-[:FAVORITE]->(p:FarmProduct)
        RETURN p.uid as uid
        """
        results = session.run(query, {"user_uid": user_uid})

        favorites = []
        for record in results:
            product = _retry_get_or_none(FarmProduct, uid=record["uid"])
            if product:
                favorites.append(
                    FarmProductController._to_response(product)  # 🔥 reuse formatter
                )

        return favorites
    print("i reach the controller frontline")
    driver = get_db()
    with driver.session() as session:
        query = """
        MATCH (u:User {uid: $user_uid})-[:FAVORITE]->(p:FarmProduct)
        OPTIONAL MATCH (p)-[:SOLD_BY]->(s:User)
        RETURN p.uid as uid,
            p.name as name,
            p.price as price,
            p.quantity as quantity,
            p.description as description,
            p.category as category,
            p.image_url as image_url,
            p.created_at as created_at,
            s.uid as seller_uid,
            s.full_name as seller_name
        """
        results = session.run(query, {"user_uid": user_uid})
        print("i reach the controller after query")

        favorites = []
        for record in results:
            favorites.append({
                "uid": record["uid"],
                "name": record["name"],
                "price": record["price"],
                "quantity": record["quantity"],
                "description": record["description"] or "",
                "category": record["category"] or "",
                "image_url": record["image_url"] or "",
                "seller_uid": record["seller_uid"] or "",
                "seller_name": record["seller_name"] or "",
                "created_at": record["created_at"]
            })
        print("i reach the controller before return")

        return favorites
    
def is_favorited(user_uid: str, product_uid: str) -> bool:
    driver = get_db()
    with driver.session() as session:
        query = """
        MATCH (u:User {uid: $user_uid})-[f:FAVORITE]->(p:FarmProduct {uid: $product_uid})
        RETURN COUNT(f) > 0 AS is_favorited
        """
        result = session.run(query, {
            "user_uid": user_uid,
            "product_uid": product_uid
        }).single()

        return result["is_favorited"] if result else False