from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from ..schemas import OrderCreate, OrderStatusUpdate, OrderResponse, NotificationCreate
from ..controllers.notification_controller import NotificationController
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
    seller_uid: str
    order_uid: str
    product_uid: Optional[str] = None
    product_name: Optional[str] = None
    rating: int
    comment: str
    created_at: str
    updated_at: str
class ReviewUpdate(BaseModel):
    rating: int
    comment: Optional[str] = ""


@router.put("/{review_uid}", response_model=ReviewResponse)
def edit_review(review_uid: str, review: ReviewUpdate):
    """Edit an existing review"""

    driver = get_db()

    with driver.session() as session:

        # Check if review exists
        check_query = """
        MATCH (r:Review {uid: $review_uid})
        RETURN r
        """

        existing = session.run(check_query, {
            "review_uid": review_uid
        }).single()

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="Review not found"
            )

        now = datetime.utcnow().isoformat()

        # Update review
        update_query = """
        MATCH (r:Review {uid: $review_uid})

        SET
            r.rating = $rating,
            r.comment = $comment,
            r.updated_at = $updated_at

        RETURN
            r.uid AS uid,
            r.buyer_uid AS buyer_uid,
            r.buyer_name AS buyer_name,
            r.seller_uid AS seller_uid,
            r.order_uid AS order_uid,
            r.product_uid AS product_uid,
            r.product_name AS product_name,
            r.rating AS rating,
            r.comment AS comment,
            r.created_at AS created_at,
            r.updated_at AS updated_at
        """

        result = session.run(update_query, {
            "review_uid": review_uid,
            "rating": review.rating,
            "comment": review.comment,
            "updated_at": now
        })

        record = result.single()

        return {
            "uid": record["uid"],
            "buyer_uid": record["buyer_uid"],
            "buyer_name": record["buyer_name"],
            "seller_uid": record["seller_uid"],
            "order_uid": record["order_uid"],
            "product_uid": record.get("product_uid"),
            "product_name": record.get("product_name"),
            "rating": record["rating"],
            "comment": record["comment"],
            "created_at": record["created_at"],
            "updated_at": record["updated_at"],
        }

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

        existing = session.run(check_query, {
            "order_uid": review.order_uid
        })

        if existing.single():
            raise HTTPException(
                status_code=400,
                detail="Review already submitted for this order"
            )

        review_uid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        # Get product info
        derive_query = """
        MATCH (o:Order {uid: $order_uid})
        OPTIONAL MATCH (o)-[:CONTAINS]->(p:FarmProduct)
        RETURN
          p.uid AS product_uid,
          p.name AS product_name
        """

        derived = session.run(
            derive_query,
            {"order_uid": review.order_uid}
        ).single()

        derived_product_uid = None
        derived_product_name = None

        if derived:
            derived_product_uid = derived.get("product_uid")
            derived_product_name = derived.get("product_name")

        final_product_uid = derived_product_uid or review.product_uid

        # Create review
        create_query = """
        CREATE (r:Review {
            uid: $uid,
            buyer_uid: $buyer_uid,
            buyer_name: $buyer_name,
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
               r.seller_uid AS seller_uid, r.order_uid AS order_uid,
               r.product_uid AS product_uid, r.product_name AS product_name,
               r.rating AS rating, r.comment AS comment,
               r.created_at AS created_at, r.updated_at AS updated_at
        """

        result = session.run(create_query, {
            "uid": review_uid,
            "buyer_uid": review.buyer_uid,
            "buyer_name": review.buyer_name,
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

        # ================================
        # FIXED NOTIFICATION (ONLY THIS)
        # ================================
        NotificationController.create_notification(
            NotificationCreate(
                recipient_uid=review.seller_uid,
                sender_name=review.buyer_name,
                product_name=derived_product_name,
                type="new_review"
            )
        )

        return {
            "uid": record["uid"],
            "buyer_uid": record["buyer_uid"],
            "buyer_name": record["buyer_name"],
            "seller_uid": record["seller_uid"],
            "order_uid": record["order_uid"],
            "product_uid": record.get("product_uid"),
            "product_name": record.get("product_name"),
            "rating": record["rating"],
            "comment": record["comment"],
            "created_at": record["created_at"],
            "updated_at": record.get("updated_at") or record["created_at"],
        }
@router.get("/product/{product_uid}/summary")
def get_product_rating_summary(product_uid: str):
    """Get rating summary for a specific product"""

    driver = get_db()

    with driver.session() as session:

        query = """
        MATCH (r:Review {product_uid: $product_uid})

        RETURN
            avg(r.rating) AS average_rating,
            count(r) AS total_reviews
        """

        result = session.run(query, {
            "product_uid": product_uid
        })

        record = result.single()

        if not record:
            return {
                "product_uid": product_uid,
                "average_rating": 0,
                "review_count": 0
            }

        return {
            "product_uid": product_uid,
            "average_rating": record["average_rating"] or 0,
            "review_count": record["total_reviews"] or 0
        }


@router.get("/product/{product_uid}", response_model=List[ReviewResponse])
def get_product_reviews(product_uid: str):
    """Get all reviews for a specific product"""

    driver = get_db()

    with driver.session() as session:

        query = """
        MATCH (r:Review {product_uid: $product_uid})

        RETURN
            r.uid AS uid,
            r.buyer_uid AS buyer_uid,
            r.buyer_name AS buyer_name,
            r.seller_uid AS seller_uid,
            r.order_uid AS order_uid,
            r.product_uid AS product_uid,
            r.product_name AS product_name,
            r.rating AS rating,
            r.comment AS comment,
            r.created_at AS created_at,
            r.updated_at AS updated_at

        ORDER BY r.created_at DESC
        """

        result = session.run(query, {
            "product_uid": product_uid
        })

        reviews = []

        for record in result:

            reviews.append({
                "uid": record["uid"],
                "buyer_uid": record["buyer_uid"],
                "buyer_name": record["buyer_name"],
                "seller_uid": record["seller_uid"],
                "order_uid": record["order_uid"],
                "product_uid": record["product_uid"],
                "product_name": record["product_name"],
                "rating": record["rating"],
                "comment": record["comment"],
                "created_at": record["created_at"],
                "updated_at": record.get("updated_at") or record["created_at"],
            })

        return reviews
# Get reviews for a seller
@router.get("/seller/{seller_uid}", response_model=List[ReviewResponse])
def get_seller_reviews(seller_uid: str):
    """Get all reviews for a seller"""
    driver = get_db()
    with driver.session() as session:
        query = """
        MATCH (r:Review {seller_uid: $seller_uid})
        RETURN r.uid AS uid, r.buyer_uid AS buyer_uid, r.buyer_name AS buyer_name,
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
        # Calculate rating from reviews directly
        query = """
        MATCH (r:Review {seller_uid: $seller_uid})
        RETURN avg(r.rating) AS average_rating, 
               count(r) AS total_reviews
        """
        result = session.run(query, {"seller_uid": seller_uid})
        record = result.single()
        
        if not record:
            return {
                "seller_uid": seller_uid,
                "average_rating": 0,
                "review_count": 0
            }
        
        return {
            "seller_uid": seller_uid,
            "average_rating": record["average_rating"] or 0,
            "review_count": record["total_reviews"] or 0
        }


@router.get("/deals")
def get_deals():
    from neomodel import db
    from datetime import datetime, timezone

    query = """
    MATCH (d:Deal)
    RETURN d.deal_id, d.percentage, d.type,
           d.created_at, d.expires_at
    ORDER BY d.created_at DESC
    """

    results, _ = db.cypher_query(query)

    deals = []

    # IMPORTANT FIX: timezone-aware now
    now = datetime.now(timezone.utc)

    for row in results:
        deal_id = row[0]
        percentage = row[1]
        deal_type = row[2]
        created_at = row[3]
        expires_at = row[4]

        # Convert Neo4j datetime safely
        try:
            expires_at_dt = expires_at.to_native()
        except Exception:
            expires_at_dt = expires_at

        # Ensure timezone consistency
        if expires_at_dt.tzinfo is None:
            expires_at_dt = expires_at_dt.replace(tzinfo=timezone.utc)

        # Compute remaining time
        remaining = expires_at_dt - now

        if remaining.total_seconds() <= 0:
            status = "expired"
            time_left = "0"
        else:
            status = "active"
            time_left = str(remaining)

        deals.append({
            "deal_id": deal_id,
            "percentage": percentage,
            "type": deal_type,
            "status": status,
            "time_left": time_left
        })

    return deals