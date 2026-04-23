from fastapi import APIRouter, Depends
from ..schemas import UserResponse
from ..utils.dependencies import get_current_user
from ..models.user import User

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
