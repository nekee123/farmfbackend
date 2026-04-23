from typing import List, Optional
from fastapi import HTTPException, status
from neo4j import exceptions as neo4j_exceptions
import time
from ..models import FarmProduct, User
from ..utils.dependencies import _retry_get_or_none
from ..schemas import FarmProductCreate, FarmProductUpdate, FarmProductResponse
from ..database import get_db


class FarmProductController:
    """Controller for Farm Product CRUD operations using unified User model"""
    
    @staticmethod
    def create_product(product_data: FarmProductCreate, current_user: User) -> FarmProductResponse:
        """Create a new farm product for the current authenticated seller"""
        attempts = 3
        backoff = 0.5
        last_exc = None

        for attempt in range(attempts):
            try:
                # Create new product with seller info from current_user
                product = FarmProduct(
                    name=product_data.name,
                    type=product_data.type,
                    price=product_data.price,
                    quantity=product_data.quantity,
                    description=product_data.description,
                    image=product_data.image if product_data.image else "",
                    payment_methods=product_data.payment_methods if product_data.payment_methods else "CASH_ON_DELIVERY,MEET_UP_CASH_ON_PICKUP",
                    seller_uid=current_user.uid  # Store seller UID directly
                ).save()

                # Link to current user as seller (maintain relationship for queries)
                product.seller.connect(current_user)

                return FarmProductController._to_response(product)
                
            except neo4j_exceptions.ServiceUnavailable as e:
                last_exc = e
                if attempt < attempts - 1:
                    time.sleep(backoff * (attempt + 1))
                    continue
                else:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Database unavailable, please try again later"
                    ) from e
            except neo4j_exceptions.SessionExpired as e:
                last_exc = e
                if attempt < attempts - 1:
                    time.sleep(backoff * (attempt + 1))
                    continue
                else:
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Database session expired, please try again later"
                    ) from e
        
        # This should never be reached, but just in case
        if last_exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database operation failed, please try again later"
            ) from last_exc
    
    @staticmethod
    def get_product(product_uid: str) -> FarmProductResponse:
        """Get product by UID"""
        product = _retry_get_or_none(FarmProduct, uid=product_uid)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return FarmProductController._to_response(product)
    
    @staticmethod
    def get_all_products(
        name: Optional[str] = None,
        type: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        seller_uid: Optional[str] = None
    ) -> List[FarmProductResponse]:
        """Get all products with optional filters using unified User model"""
        # Use Cypher query to get products with seller info in one go
        driver = get_db()
        with driver.session() as session:
            # Build base query - matching SOLD_BY relationship to User node
            query = """
            MATCH (p:FarmProduct)
            OPTIONAL MATCH (p)-[:SOLD_BY]->(u:User)
            """

            # Build WHERE clause
            where_conditions = []
            params = {}

            if name:
                where_conditions.append("toLower(p.name) CONTAINS toLower($name)")
                params["name"] = name

            if type:
                where_conditions.append("toLower(p.type) CONTAINS toLower($type)")
                params["type"] = type

            if min_price is not None:
                where_conditions.append("p.price >= $min_price")
                params["min_price"] = min_price

            if max_price is not None:
                where_conditions.append("p.price <= $max_price")
                params["max_price"] = max_price

            if seller_uid:
                where_conditions.append("u.uid = $seller_uid")
                params["seller_uid"] = seller_uid

            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)

            # Return results
            query += """
            RETURN p.uid as uid, p.name as name, p.type as type, p.price as price,
                   p.quantity as quantity, p.description as description, p.image as image,
                   p.payment_methods as payment_methods, p.seller_uid as seller_uid,
                   p.created_at as created_at, p.updated_at as updated_at,
                   u.uid as seller_uid_rel, u.full_name as seller_name, u.location as seller_location,
                   u.phone_number as seller_contact, u.profile_picture as seller_profile_picture
            ORDER BY p.created_at DESC
            """
            
            results = session.run(query, params)

            products = []
            for record in results:
                products.append(FarmProductResponse(
                    uid=record["uid"],
                    name=record["name"],
                    type=record["type"],
                    price=record["price"],
                    quantity=record["quantity"],
                    description=record["description"] or "",
                    image=record["image"] or "",
                    payment_methods=record["payment_methods"] or "CASH_ON_DELIVERY,MEET_UP_CASH_ON_PICKUP",
                    seller_uid=record["seller_uid"] or record["seller_uid_rel"] or "",
                    seller_name=record["seller_name"],
                    seller_location=record["seller_location"],
                    seller_contact=record.get("seller_contact"),
                    seller_profile_picture=record.get("seller_profile_picture"),
                    created_at=record["created_at"],
                    updated_at=record["updated_at"]
                ))
            
            return products
    
    @staticmethod
    def update_product(product_uid: str, product_data: FarmProductUpdate, current_user: User) -> FarmProductResponse:
        """Update product information (owner or admin)"""
        product = _retry_get_or_none(FarmProduct, uid=product_uid)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Check ownership (admins can update any product)
        if current_user.role != "admin":
            sellers = product.seller.all()
            if not sellers or sellers[0].uid != current_user.uid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only update your own products"
                )

        # Update fields if provided
        if product_data.name is not None:
            product.name = product_data.name
        if product_data.type is not None:
            product.type = product_data.type
        if product_data.price is not None:
            product.price = product_data.price
        if product_data.quantity is not None:
            product.quantity = product_data.quantity
        if product_data.description is not None:
            product.description = product_data.description
        if product_data.image is not None:
            product.image = product_data.image
        if product_data.payment_methods is not None:
            product.payment_methods = product_data.payment_methods

        product.update_timestamp()
        return FarmProductController._to_response(product)
    
    @staticmethod
    def delete_product(product_uid: str, current_user: User) -> dict:
        """Delete a product (owner or admin)"""
        product = _retry_get_or_none(FarmProduct, uid=product_uid)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        # Check ownership (admins can delete any product)
        if current_user.role != "admin":
            sellers = product.seller.all()
            if not sellers or sellers[0].uid != current_user.uid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only delete your own products"
                )

        product.delete()
        return {"message": "Product deleted successfully"}
    
    @staticmethod
    def _to_response(product: FarmProduct) -> FarmProductResponse:
        """Convert FarmProduct model to response schema using unified User model"""
        # Get the seller relationship
        sellers = product.seller.all()
        seller = sellers[0] if sellers else None

        return FarmProductResponse(
            uid=product.uid,
            name=product.name,
            type=product.type,
            price=product.price,
            quantity=product.quantity,
            description=product.description,
            image=product.image if hasattr(product, 'image') else "",
            payment_methods=product.payment_methods if hasattr(product, 'payment_methods') else "CASH_ON_DELIVERY,MEET_UP_CASH_ON_PICKUP",
            seller_uid=product.seller_uid if hasattr(product, 'seller_uid') and product.seller_uid else (seller.uid if seller else ""),
            seller_name=seller.full_name if seller else None,
            seller_location=seller.location if seller else None,
            seller_contact=seller.phone_number if seller else None,
            seller_profile_picture=seller.profile_picture if seller else None,
            created_at=product.created_at,
            updated_at=product.updated_at
        )
