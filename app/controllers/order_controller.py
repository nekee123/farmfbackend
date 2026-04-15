from typing import List
from fastapi import HTTPException, status
from ..models import Order, FarmProduct, Buyer, Seller
from ..utils.dependencies import _retry_get_or_none
from ..schemas import OrderCreate, OrderStatusUpdate, OrderResponse
from ..database import get_db
from datetime import datetime
import uuid


class OrderController:
    """Controller for Order CRUD operations"""
    
    @staticmethod
    def create_order(order_data: OrderCreate) -> OrderResponse:
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
        
        # Lookup buyer
        buyer = _retry_get_or_none(Buyer, uid=order_data.buyer_uid)
        if not buyer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buyer not found")
        
        if product.quantity < order_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient quantity. Available: {product.quantity}"
            )
        
        # Get seller
        sellers = product.seller.all()
        if not sellers:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product has no seller")
        seller = sellers[0]
        
        total_price = product.price * order_data.quantity
        
        # Create order with payment method and default status
        order = Order(
            quantity=order_data.quantity, 
            total_price=total_price, 
            payment_method=order_data.payment_method,
            order_status="Pending"
        ).save()
        order.buyer.connect(buyer)
        order.seller.connect(seller)
        order.farm_product.connect(product)
        product.reduce_quantity(order_data.quantity)
        
        # Create notification for seller
        OrderController._create_notification(
            recipient_uid=seller.uid,
            recipient_type="seller",
            notif_type="new_order",
            message=f"New order received from {buyer.name} for {product.name}!"
        )
        
        return OrderController._to_response(order)
    
    @staticmethod
    def get_order(order_uid: str) -> OrderResponse:
        order = Order.nodes.get_or_none(uid=order_uid)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return OrderController._to_response(order)
    
    @staticmethod
    def get_all_orders() -> List[OrderResponse]:
        """Get all orders using direct Cypher query"""
        driver = get_db()
        with driver.session() as session:
            query = """
            MATCH (o:Order)
            OPTIONAL MATCH (o)-[:PLACED_BY]->(b:Buyer)
            OPTIONAL MATCH (o)-[:FULFILLED_BY]->(s:Seller)
            OPTIONAL MATCH (o)-[:CONTAINS]->(p:FarmProduct)
            OPTIONAL MATCH (r:Review {order_uid: o.uid})
            RETURN o.uid as uid, o.quantity as quantity, o.total_price as total_price,
                   o.order_status as order_status, o.payment_method as payment_method,
                   o.created_at as created_at, o.updated_at as updated_at,
                   b.uid as buyer_uid, b.name as buyer_name, b.phone_number as buyer_contact,
                   s.uid as seller_uid, s.name as seller_name, s.phone_number as seller_contact,
                   p.uid as farm_product_uid, p.name as farm_product_name,
                   count(r) > 0 as is_reviewed
            ORDER BY o.created_at DESC
            """
            
            results = session.run(query)
            
            orders = []
            for record in results:
                orders.append({
                    "uid": record["uid"],
                    "buyer_uid": record["buyer_uid"] or "",
                    "buyer_name": record["buyer_name"] or "",
                    "buyer_contact": record["buyer_contact"] or "N/A",
                    "seller_uid": record["seller_uid"] or "",
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
    def get_buyer_orders(buyer_uid: str) -> List[OrderResponse]:
        """Get buyer orders using direct Cypher query"""
        driver = get_db()
        with driver.session() as session:
            query = """
            MATCH (b:Buyer {uid: $buyer_uid})-[:PLACED_BY]-(o:Order)
            OPTIONAL MATCH (o)-[:FULFILLED_BY]->(s:Seller)
            OPTIONAL MATCH (o)-[:CONTAINS]->(p:FarmProduct)
            OPTIONAL MATCH (r:Review {order_uid: o.uid})
            RETURN o.uid as uid, o.quantity as quantity, o.total_price as total_price,
                   o.order_status as order_status, o.payment_method as payment_method,
                   o.created_at as created_at, o.updated_at as updated_at,
                   b.uid as buyer_uid, b.name as buyer_name, b.phone_number as buyer_contact,
                   s.uid as seller_uid, s.name as seller_name, s.phone_number as seller_contact,
                   p.uid as farm_product_uid, p.name as farm_product_name,
                   count(r) > 0 as is_reviewed
            ORDER BY o.created_at DESC
            """
            
            results = session.run(query, {"buyer_uid": buyer_uid})
            
            orders = []
            for record in results:
                orders.append({
                    "uid": record["uid"],
                    "buyer_uid": record["buyer_uid"] or "",
                    "buyer_name": record["buyer_name"] or "",
                    "buyer_contact": record["buyer_contact"] or "N/A",
                    "seller_uid": record["seller_uid"] or "",
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
    def get_seller_orders(seller_uid: str) -> List[OrderResponse]:
        """Get seller orders using direct Cypher query"""
        driver = get_db()
        with driver.session() as session:
            query = """
            MATCH (s:Seller {uid: $seller_uid})-[:FULFILLED_BY]-(o:Order)
            OPTIONAL MATCH (o)-[:PLACED_BY]->(b:Buyer)
            OPTIONAL MATCH (o)-[:CONTAINS]->(p:FarmProduct)
            OPTIONAL MATCH (r:Review {order_uid: o.uid})
            RETURN o.uid as uid, o.quantity as quantity, o.total_price as total_price,
                   o.order_status as order_status, o.payment_method as payment_method,
                   o.created_at as created_at, o.updated_at as updated_at,
                   b.uid as buyer_uid, b.name as buyer_name, b.phone_number as buyer_contact,
                   s.uid as seller_uid, s.name as seller_name, s.phone_number as seller_contact,
                   p.uid as farm_product_uid, p.name as farm_product_name,
                   count(r) > 0 as is_reviewed
            ORDER BY o.created_at DESC
            """
            
            results = session.run(query, {"seller_uid": seller_uid})
            
            orders = []
            for record in results:
                orders.append({
                    "uid": record["uid"],
                    "buyer_uid": record["buyer_uid"] or "",
                    "buyer_name": record["buyer_name"] or "",
                    "buyer_contact": record["buyer_contact"] or "N/A",
                    "seller_uid": record["seller_uid"] or "",
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
    def delete_order(order_uid: str) -> dict:
        order = _retry_get_or_none(Order, uid=order_uid)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
        if order.order_status == "Pending":
            products = order.farm_product.all()
            if products:
                product = products[0]
                product.quantity += order.quantity
                product.update_timestamp()
        
        order.delete()
        return {"message": "Order deleted successfully"}
    
    @staticmethod
    def _create_notification(recipient_uid: str, recipient_type: str, notif_type: str, message: str):
        """Helper method to create a notification"""
        try:
            driver = get_db()
            with driver.session() as session:
                notif_uid = str(uuid.uuid4())
                created_at = datetime.utcnow().isoformat()
                
                query = """
                CREATE (n:Notification {
                    uid: $uid,
                    recipient_uid: $recipient_uid,
                    recipient_type: $recipient_type,
                    type: $type,
                    message: $message,
                    read: false,
                    created_at: $created_at
                })
                """
                
                session.run(query, {
                    "uid": notif_uid,
                    "recipient_uid": recipient_uid,
                    "recipient_type": recipient_type,
                    "type": notif_type,
                    "message": message,
                    "created_at": created_at
                })
        except Exception as e:
            print(f"Error creating notification: {e}")
    
    @staticmethod
    def _to_response(order: Order) -> dict:
        """Convert Order model to response dictionary including buyer and seller contacts"""
         # Get related buyer, seller, and product
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
        "buyer_uid": buyer.uid if buyer else "",
        "buyer_name": buyer.name if buyer else "",
        "buyer_contact": buyer.phone_number if buyer else "N/A",
        "seller_uid": seller.uid if seller else "",
        "seller_name": seller.name if seller else "",
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
    def update_order_status(order_uid: str, status_data: OrderStatusUpdate) -> dict:
        """Update order status"""
        # Validate allowed statuses
        allowed_statuses = ["Pending", "Confirmed", "Cancelled", "Delivered"]
        if status_data.order_status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order status must be one of: {', '.join(allowed_statuses)}"
            )
        
        # Find order
        order = _retry_get_or_none(Order, uid=order_uid)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Prevent changing from Delivered back to other statuses
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
        
        # Update status
        order.order_status = status_data.order_status
        order.update_timestamp()
        
        return {
            "message": "Order status updated successfully",
            "order_uid": order.uid,
            "order_status": order.order_status
        }