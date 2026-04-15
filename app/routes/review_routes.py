from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from ..database import get_db
import uuid

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

# Pydantic models
class ReviewCreate(BaseModel):
    buyer_uid: str
    buyer_name: str
    seller_uid: str
    order_uid: str
    # Optional: the Flutter app sends this as farm_product_uid/product_uid.
    # We keep it optional and primarily derive product info from the order graph.
    product_uid: Optional[str] = None
    rating: int
    comment: Optional[str] = ""

class ReviewResponse(BaseModel):
    uid: str
    buyer_uid: str
    buyer_name: str
    buyer_profile_picture: Optional[str] = None
    seller_uid: str
    order_uid: str
    product_uid: Optional[str] = None
    product_name: Optional[str] = None
    rating: int
    comment: str
    created_at: str
    updated_at: str

# Submit review
@router.post("/", response_model=ReviewResponse)
def submit_review(review: ReviewCreate):
    """Submit a review for a seller"""
    driver = get_db()
    with driver.session() as session:
        # Check if review already exists for this order
        check_query = """
        MATCH (r:Review {order_uid: $order_uid})
        RETURN r.uid AS uid
        """
        existing = session.run(check_query, {"order_uid": review.order_uid})
        if existing.single():
            raise HTTPException(status_code=400, detail="Review already submitted for this order")
        
        review_uid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        # Derive buyer profile picture + product info from the graph (best-effort).
        # This prevents frontend parsing issues when these fields are missing.
        derive_query = """
        MATCH (o:Order {uid: $order_uid})
        OPTIONAL MATCH (o)-[:CONTAINS]->(p:FarmProduct)
        OPTIONAL MATCH (b:Buyer {uid: $buyer_uid})
        RETURN
          p.uid AS product_uid,
          p.name AS product_name,
          b.profile_picture AS buyer_profile_picture
        """
        derived = session.run(
            derive_query,
            {"order_uid": review.order_uid, "buyer_uid": review.buyer_uid},
        ).single()

        derived_product_uid = None
        derived_product_name = None
        derived_buyer_profile_picture = None
        if derived:
            derived_product_uid = derived.get("product_uid")
            derived_product_name = derived.get("product_name")
            derived_buyer_profile_picture = derived.get("buyer_profile_picture")

        final_product_uid = derived_product_uid or review.product_uid
        
        # Create review
        create_query = """
        CREATE (r:Review {
            uid: $uid,
            buyer_uid: $buyer_uid,
            buyer_name: $buyer_name,
            buyer_profile_picture: $buyer_profile_picture,
            seller_uid: $seller_uid,
            order_uid: $order_uid,
            product_uid: $product_uid,
            product_name: $product_name,
            rating: $rating,
            comment: $comment,
            created_at: $created_at,
            updated_at: $updated_at
        })
        RETURN r.uid AS uid, r.buyer_uid AS buyer_uid, r.buyer_name AS buyer_name,
               r.buyer_profile_picture AS buyer_profile_picture,
               r.seller_uid AS seller_uid, r.order_uid AS order_uid,
               r.product_uid AS product_uid, r.product_name AS product_name,
               r.rating AS rating, r.comment AS comment,
               r.created_at AS created_at, r.updated_at AS updated_at
        """
        
        result = session.run(create_query, {
            "uid": review_uid,
            "buyer_uid": review.buyer_uid,
            "buyer_name": review.buyer_name,
            "buyer_profile_picture": derived_buyer_profile_picture,
            "seller_uid": review.seller_uid,
            "order_uid": review.order_uid,
            "product_uid": final_product_uid,
            "product_name": derived_product_name,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": now,
            "updated_at": now,
        })
        
        record = result.single()
        
        # Create notification for seller
        notif_uid = str(uuid.uuid4())
        notif_message = f"{review.buyer_name} left a {review.rating}-star review!"
        
        notif_query = """
        CREATE (n:Notification {
            uid: $uid,
            recipient_uid: $seller_uid,
            recipient_type: 'seller',
            type: 'new_review',
            message: $message,
            read: false,
            created_at: $created_at
        })
        """
        
        session.run(notif_query, {
            "uid": notif_uid,
            "seller_uid": review.seller_uid,
            "message": notif_message,
            "created_at": now
        })
        
        # Update seller's average rating
        update_rating_query = """
        MATCH (s:Seller {uid: $seller_uid})
        OPTIONAL MATCH (r:Review {seller_uid: $seller_uid})
        WITH s, avg(r.rating) AS avg_rating, count(r) AS review_count
        SET s.average_rating = avg_rating,
            s.review_count = review_count
        """
        session.run(update_rating_query, {"seller_uid": review.seller_uid})
        
        return {
            "uid": record["uid"],
            "buyer_uid": record["buyer_uid"],
            "buyer_name": record["buyer_name"],
            "buyer_profile_picture": record.get("buyer_profile_picture"),
            "seller_uid": record["seller_uid"],
            "order_uid": record["order_uid"],
            "product_uid": record.get("product_uid"),
            "product_name": record.get("product_name"),
            "rating": record["rating"],
            "comment": record["comment"],
            "created_at": record["created_at"],
            "updated_at": record.get("updated_at") or record["created_at"],
        }

# Get reviews for a seller
@router.get("/seller/{seller_uid}", response_model=List[ReviewResponse])
def get_seller_reviews(seller_uid: str):
    """Get all reviews for a seller"""
    driver = get_db()
    with driver.session() as session:
        query = """
        MATCH (r:Review {seller_uid: $seller_uid})
        RETURN r.uid AS uid, r.buyer_uid AS buyer_uid, r.buyer_name AS buyer_name,
               r.buyer_profile_picture AS buyer_profile_picture,
               r.seller_uid AS seller_uid, r.order_uid AS order_uid,
               r.product_uid AS product_uid, r.product_name AS product_name,
               r.rating AS rating, r.comment AS comment,
               r.created_at AS created_at, r.updated_at AS updated_at
        ORDER BY r.created_at DESC
        """
        result = session.run(query, {"seller_uid": seller_uid})
        reviews = []
        for record in result:
            reviews.append({
                "uid": record["uid"],
                "buyer_uid": record["buyer_uid"],
                "buyer_name": record["buyer_name"],
                "buyer_profile_picture": record.get("buyer_profile_picture"),
                "seller_uid": record["seller_uid"],
                "order_uid": record["order_uid"],
                "product_uid": record.get("product_uid"),
                "product_name": record.get("product_name"),
                "rating": record["rating"],
                "comment": record["comment"],
                "created_at": record["created_at"],
                "updated_at": record.get("updated_at") or record["created_at"],
            })
        return reviews

# Get seller rating summary
@router.get("/seller/{seller_uid}/summary")
def get_seller_rating_summary(seller_uid: str):
    """Get rating summary for a seller"""
    driver = get_db()
    with driver.session() as session:
        query = """
        MATCH (s:Seller {uid: $seller_uid})
        OPTIONAL MATCH (r:Review {seller_uid: $seller_uid})
        RETURN s.average_rating AS average_rating, 
               s.review_count AS review_count,
               count(r) AS total_reviews
        """
        result = session.run(query, {"seller_uid": seller_uid})
        record = result.single()
        
        if not record:
            raise HTTPException(status_code=404, detail="Seller not found")
        
        return {
            "seller_uid": seller_uid,
            "average_rating": record["average_rating"] or 0,
            "review_count": record["review_count"] or 0
        }
