from typing import List, Optional
from fastapi import HTTPException, status
from neomodel import db
from neo4j import exceptions as neo4j_exceptions
import time
from ..models import Seller
from ..schemas import SellerCreate, SellerUpdate, SellerResponse
from ..utils.security import get_password_hash


class SellerController:
    """Controller for Seller CRUD operations"""
    
    @staticmethod
    def create_seller(seller_data: SellerCreate) -> SellerResponse:
        """Create a new seller"""
        # Check if phone number already exists
        existing_seller = Seller.nodes.get_or_none(phone_number=seller_data.phone_number)
        if existing_seller:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        
        # Create new seller
        seller = Seller(
            name=seller_data.name,
            phone_number=seller_data.phone_number,
            location=seller_data.location or "",
            password_hash=get_password_hash(seller_data.password)
        ).save()
        
        return SellerController._to_response(seller)
    
    @staticmethod
    def get_seller(seller_uid: str) -> SellerResponse:
        """Get seller by UID"""
        seller = Seller.nodes.get_or_none(uid=seller_uid)
        if not seller:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seller not found"
            )
        return SellerController._to_response(seller)
    
    @staticmethod
    def get_all_sellers() -> List[SellerResponse]:
        """Get all sellers"""
        # Return only sellers with valid phone number format
        query = """
        MATCH (s:Seller)
        WHERE s.phone_number =~ '09[0-9]{9}'
        RETURN s.uid AS uid, s.name AS name, s.phone_number AS phone_number,
               s.location AS location, s.profile_picture AS profile_picture,
               s.created_at AS created_at, s.updated_at AS updated_at
        ORDER BY s.created_at DESC
        """

        # Retry a few times for transient DB connection issues
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
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Database unavailable, please try again later") from last_exc
        sellers = []
        for row in results:
            sellers.append({
                "uid": row[0],
                "name": row[1],
                "phone_number": row[2],
                "location": row[3] or "",
                "profile_picture": row[4],
                "created_at": row[5],
                "updated_at": row[6],
            })

        return sellers
    
    @staticmethod
    def update_seller(seller_uid: str, seller_data: SellerUpdate) -> SellerResponse:
        """Update seller information"""
        try:
            seller = Seller.nodes.get_or_none(uid=seller_uid)
        except neo4j_exceptions.ServiceUnavailable as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Database unavailable, please try again later") from e
        if not seller:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seller not found"
            )
        
        # Update fields if provided
        if seller_data.name is not None:
            seller.name = seller_data.name
        if seller_data.phone_number is not None:
            # Check if new phone number already exists
            existing = Seller.nodes.get_or_none(phone_number=seller_data.phone_number)
            if existing and existing.uid != seller_uid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already in use"
                )
            seller.phone_number = seller_data.phone_number
        if seller_data.location is not None:
            seller.location = seller_data.location
        if seller_data.password is not None:
            seller.password_hash = get_password_hash(seller_data.password)
        if seller_data.profile_picture is not None:
            seller.profile_picture = seller_data.profile_picture
        
        seller.update_timestamp()
        return SellerController._to_response(seller)
    
    @staticmethod
    def delete_seller(seller_uid: str) -> dict:
        """Delete a seller"""
        seller = Seller.nodes.get_or_none(uid=seller_uid)
        if not seller:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seller not found"
            )
        
        seller.delete()
        return {"message": "Seller deleted successfully"}
    
    @staticmethod
    def _to_response(seller: Seller) -> SellerResponse:
        """Convert Seller model to response schema"""
        return SellerResponse(
            uid=seller.uid,
            name=seller.name,
            phone_number=seller.phone_number,
            location=seller.location if hasattr(seller, 'location') else "",
            profile_picture=seller.profile_picture if hasattr(seller, 'profile_picture') else "",
            created_at=seller.created_at,
            updated_at=seller.updated_at
        )
