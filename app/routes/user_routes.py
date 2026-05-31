from fastapi import APIRouter, Depends
from ..schemas import UserResponse
from ..utils.dependencies import get_current_user
from ..models.user import User
from fastapi import APIRouter, HTTPException
router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile data
    """
    return UserResponse(
        uid=current_user.uid,
        phone_number=current_user.phone_number,
        full_name=current_user.full_name,
        location=current_user.location,
        role=current_user.role,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )
@router.get("/seller/{seller_uid}/category")
def get_seller_category(seller_uid: str):
    from neomodel import db

    query = """
    MATCH (u:User {uid: $seller_uid})
    RETURN u.category AS category
    """

    results, _ = db.cypher_query(query, {
        "seller_uid": seller_uid
    })

    if not results:
        raise HTTPException(
            status_code=404,
            detail="Seller not found"
        )

    return {
        "category": results[0][0] or []
    }