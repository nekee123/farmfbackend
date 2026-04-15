from typing import List, Optional
from fastapi import HTTPException, status
from neo4j import exceptions as neo4j_exceptions
import time
from ..models import FarmProduct, Seller
from ..utils.dependencies import _retry_get_or_none
from ..schemas import FarmProductCreate, FarmProductUpdate, FarmProductResponse
from ..database import get_db


class FarmProductController:
    """Controller for Farm Product CRUD operations"""
    
    @staticmethod
    def create_product(product_data: FarmProductCreate) -> FarmProductResponse:
        """Create a new farm product"""
        attempts = 3
        backoff = 0.5
        last_exc = None
        
        for attempt in range(attempts):
            try:
                # Get the seller
                seller = _retry_get_or_none(Seller, uid=product_data.seller_uid)
                if not seller:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Seller not found"
                    )
                
                # Create new product
                product = FarmProduct(
                    name=product_data.name,
                    type=product_data.type,
                    price=product_data.price,
                    quantity=product_data.quantity,
                    description=product_data.description,
                    image=product_data.image if product_data.image else "",
                    payment_methods=product_data.payment_methods if product_data.payment_methods else "CASH_ON_DELIVERY,MEET_UP_CASH_ON_PICKUP",
                    seller_uid=product_data.seller_uid,
                    seller_name=product_data.seller_name,
                    seller_location=seller.location if hasattr(seller, 'location') else ""
                ).save()
                
                # Link to seller using explicit SOLD_BY relationship
                # This ensures consistency with the get_all_products Cypher query
                product.seller.connect(seller)
                
                # Double check the relationship name in the database
                with get_db().session() as session:
                    session.run(
                        "MATCH (p:FarmProduct {uid: $p_uid}), (s:Seller {uid: $s_uid}) "
                        "MERGE (p)-[:SOLD_BY]->(s)",
                        p_uid=product.uid, s_uid=seller.uid
                    )
                
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
        """Get all products with optional filters"""
        # Use Cypher query to get products with seller info in one go
        driver = get_db()
        with driver.session() as session:
            # Build base query
            query = """
            MATCH (p:FarmProduct)
            OPTIONAL MATCH (p)-[:SOLD_BY|seller]->(s:Seller)
            RETURN p.uid as uid, p.name as name, p.type as type, p.price as price, 
                   p.quantity as quantity, p.description as description, p.image as image,
                   p.payment_methods as payment_methods,
                   p.created_at as created_at, p.updated_at as updated_at,
                   s.uid as seller_uid, s.name as seller_name, s.location as seller_location
            ORDER BY p.created_at DESC
            """
            
            results = session.run(query)
            
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
                    seller_uid=record["seller_uid"],
                    seller_name=record["seller_name"],
                    seller_location=record["seller_location"],
                    created_at=record["created_at"],
                    updated_at=record["updated_at"]
                ))
            
            return products
    
    @staticmethod
    def update_product(product_uid: str, product_data: FarmProductUpdate) -> FarmProductResponse:
        """Update product information"""
        product = _retry_get_or_none(FarmProduct, uid=product_uid)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
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
    def delete_product(product_uid: str) -> dict:
        """Delete a product"""
        product = _retry_get_or_none(FarmProduct, uid=product_uid)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        product.delete()
        return {"message": "Product deleted successfully"}
    
    @staticmethod
    def _to_response(product: FarmProduct) -> FarmProductResponse:
        """Convert FarmProduct model to response schema"""
        sellers = product.seller.all()
        seller_uid = sellers[0].uid if sellers else None
        seller_name = sellers[0].name if sellers else None
        seller_location = sellers[0].location if sellers and hasattr(sellers[0], 'location') else None
        
        return FarmProductResponse(
            uid=product.uid,
            name=product.name,
            type=product.type,
            price=product.price,
            quantity=product.quantity,
            description=product.description,
            image=product.image if hasattr(product, 'image') else "",
            payment_methods=product.payment_methods if hasattr(product, 'payment_methods') else "CASH_ON_DELIVERY,MEET_UP_CASH_ON_PICKUP",
            seller_uid=seller_uid,
            seller_name=seller_name,
            seller_location=seller_location,
            created_at=product.created_at,
            updated_at=product.updated_at
        )
