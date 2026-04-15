from typing import List, Optional
from fastapi import HTTPException, status
from neomodel import db
from neo4j import exceptions as neo4j_exceptions
import time
from ..models import Cart, CartItem, Buyer, FarmProduct
from ..schemas import CartItemCreate, CartItemUpdate, CartResponse, CartItemResponse, CartSummary
from ..utils.dependencies import _retry_get_or_none


class CartController:
    """Controller for Cart CRUD operations"""
    
    @staticmethod
    def get_or_create_cart(buyer_uid: str) -> Cart:
        """Get existing cart or create new one for buyer"""
        # Try to find existing cart
        query = """
        MATCH (c:Cart {buyer_uid: $buyer_uid})
        RETURN c
        """
        
        attempts = 3
        backoff = 0.5
        last_exc = None
        
        for attempt in range(attempts):
            try:
                results, meta = db.cypher_query(query, {"buyer_uid": buyer_uid})
                if results:
                    cart_node = results[0][0]
                    return Cart.inflate(cart_node)
                last_exc = None
                break
            except neo4j_exceptions.ServiceUnavailable as e:
                last_exc = e
                time.sleep(backoff * (attempt + 1))
        
        if last_exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Database unavailable, please try again later") from last_exc
        
        # Create new cart
        cart = Cart(buyer_uid=buyer_uid).save()
        return cart
    
    @staticmethod
    def add_item_to_cart(buyer_uid: str, item_data: CartItemCreate) -> CartItemResponse:
        """Add item to cart"""
        # Verify buyer exists
        buyer = _retry_get_or_none(Buyer, uid=buyer_uid)
        if not buyer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Buyer not found"
            )
        
        # Verify product exists and get current price
        product = _retry_get_or_none(FarmProduct, uid=item_data.product_uid)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Get or create cart
        cart = CartController.get_or_create_cart(buyer_uid)
        
        # Check if item already exists in cart
        existing_item_query = """
        MATCH (c:Cart {uid: $cart_uid})-[:CONTAINS]->(ci:CartItem)
        WHERE ci.product_uid = $product_uid
        RETURN ci
        """
        
        try:
            results, meta = db.cypher_query(existing_item_query, {
                "cart_uid": cart.uid,
                "product_uid": item_data.product_uid
            })
            
            if results:
                # Update existing item quantity
                existing_item = CartItem.inflate(results[0][0])
                existing_item.quantity += item_data.quantity
                existing_item.save()
                return CartController._cart_item_to_response(existing_item)
        except neo4j_exceptions.ServiceUnavailable as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Database unavailable, please try again later") from e
        
        # Create new cart item
        cart_item = CartItem(
            product_uid=item_data.product_uid,
            quantity=item_data.quantity,
            price_at_time=item_data.price_at_time
        ).save()
        
        # Create relationships
        cart.cart_items.connect(cart_item)
        cart_item.product.connect(product)
        
        cart.update_timestamp()
        
        return CartController._cart_item_to_response(cart_item)
    
    @staticmethod
    def update_cart_item(buyer_uid: str, item_uid: str, item_data: CartItemUpdate) -> CartItemResponse:
        """Update cart item quantity"""
        cart = CartController.get_or_create_cart(buyer_uid)
        
        # Find the cart item
        query = """
        MATCH (c:Cart {uid: $cart_uid})-[:CONTAINS]->(ci:CartItem {uid: $item_uid})
        RETURN ci
        """
        
        try:
            results, meta = db.cypher_query(query, {
                "cart_uid": cart.uid,
                "item_uid": item_uid
            })
            
            if not results:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cart item not found"
                )
            
            cart_item = CartItem.inflate(results[0][0])
            cart_item.quantity = item_data.quantity
            cart_item.save()
            
            cart.update_timestamp()
            
            return CartController._cart_item_to_response(cart_item)
        except neo4j_exceptions.ServiceUnavailable as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Database unavailable, please try again later") from e
    
    @staticmethod
    def remove_from_cart(buyer_uid: str, item_uid: str) -> dict:
        """Remove item from cart"""
        cart = CartController.get_or_create_cart(buyer_uid)
        
        query = """
        MATCH (c:Cart {uid: $cart_uid})-[:CONTAINS]->(ci:CartItem {uid: $item_uid})
        DETACH DELETE ci
        RETURN ci
        """
        
        try:
            results, meta = db.cypher_query(query, {
                "cart_uid": cart.uid,
                "item_uid": item_uid
            })
            
            if not results:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cart item not found"
                )
            
            cart.update_timestamp()
            
            return {"message": "Item removed from cart successfully"}
        except neo4j_exceptions.ServiceUnavailable as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Database unavailable, please try again later") from e
    
    @staticmethod
    def get_cart(buyer_uid: str) -> CartResponse:
        """Get buyer's cart with all items"""
        cart = CartController.get_or_create_cart(buyer_uid)
        
        # Get all cart items with product details
        query = """
        MATCH (c:Cart {uid: $cart_uid})-[:CONTAINS]->(ci:CartItem)-[:IS_PRODUCT]->(p:FarmProduct)
        RETURN ci, p.name as product_name, p.uid as product_uid
        ORDER BY ci.created_at DESC
        """
        
        try:
            results, meta = db.cypher_query(query, {"cart_uid": cart.uid})
            
            items = []
            total_amount = 0.0
            
            for row in results:
                cart_item = CartItem.inflate(row[0])
                item_response = CartController._cart_item_to_response(cart_item)
                items.append(item_response)
                total_amount += (cart_item.price_at_time * cart_item.quantity)
            
            return CartResponse(
                uid=cart.uid,
                buyer_uid=cart.buyer_uid,
                items=items,
                total_amount=total_amount,
                created_at=cart.created_at,
                updated_at=cart.updated_at
            )
        except neo4j_exceptions.ServiceUnavailable as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Database unavailable, please try again later") from e
    
    @staticmethod
    def clear_cart(buyer_uid: str) -> dict:
        """Clear all items from cart"""
        cart = CartController.get_or_create_cart(buyer_uid)
        
        query = """
        MATCH (c:Cart {uid: $cart_uid})-[:CONTAINS]->(ci:CartItem)
        DETACH DELETE ci
        """
        
        try:
            db.cypher_query(query, {"cart_uid": cart.uid})
            cart.update_timestamp()
            return {"message": "Cart cleared successfully"}
        except neo4j_exceptions.ServiceUnavailable as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Database unavailable, please try again later") from e
    
    @staticmethod
    def get_cart_summary(buyer_uid: str) -> CartSummary:
        """Get cart summary (item count and total)"""
        cart = CartController.get_or_create_cart(buyer_uid)
        
        query = """
        MATCH (c:Cart {uid: $cart_uid})-[:CONTAINS]->(ci:CartItem)
        RETURN count(ci) as items_count, 
               sum(ci.quantity * ci.price_at_time) as total_amount,
               sum(ci.quantity) as total_items
        """
        
        try:
            results, meta = db.cypher_query(query, {"cart_uid": cart.uid})
            
            if results and results[0][0]:
                row = results[0]
                return CartSummary(
                    total_items=row[2] or 0,
                    total_amount=row[1] or 0.0,
                    items_count=row[0] or 0
                )
            
            return CartSummary(total_items=0, total_amount=0.0, items_count=0)
        except neo4j_exceptions.ServiceUnavailable as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Database unavailable, please try again later") from e
    
    @staticmethod
    def _cart_item_to_response(cart_item: CartItem) -> CartItemResponse:
        """Convert CartItem model to response schema"""
        # Fetch product details
        product = None
        try:
            product = FarmProduct.nodes.get(uid=cart_item.product_uid)
        except FarmProduct.DoesNotExist:
            pass  # Product not found, will return None
        except neo4j_exceptions.ServiceUnavailable:
            pass  # Database error, will return None
        
        product_info = None
        if product:
            from ..schemas.cart import ProductInfo
            product_info = ProductInfo(
                uid=product.uid,
                name=product.name,
                type=product.type,
                price=product.price,
                description=product.description,
                image=product.image,
                payment_methods=product.payment_methods
            )
        
        return CartItemResponse(
            uid=cart_item.uid,
            product_uid=cart_item.product_uid,
            quantity=cart_item.quantity,
            price_at_time=cart_item.price_at_time,
            created_at=cart_item.created_at,
            product=product_info
        )
