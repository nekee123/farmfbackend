from fastapi import APIRouter, status
from typing import List
from ..schemas import SellerCreate, SellerUpdate, SellerResponse, SellerLogin
from ..controllers import SellerController

router = APIRouter(prefix="/api/sellers", tags=["Sellers"])


@router.post("/login", status_code=status.HTTP_200_OK)
def login_seller(login_data: SellerLogin):
    """
    Login as a seller - returns seller info with uid and name
    """
    from ..models import Seller
    from ..utils.security import verify_password
    from ..utils.dependencies import _retry_get_or_none
    from fastapi import HTTPException
    
    seller = _retry_get_or_none(Seller, phone_number=login_data.phone_number)
    
    if not seller or not verify_password(login_data.password, seller.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password"
        )
    
    return {
        "uid": seller.uid,
        "name": seller.name,
        "phone_number": seller.phone_number
    }


@router.post("/", response_model=SellerResponse, status_code=status.HTTP_201_CREATED)
def create_seller(seller_data: SellerCreate):
    """
    Register a new seller
    """
    return SellerController.create_seller(seller_data)


@router.get("/", response_model=List[SellerResponse])
def get_all_sellers():
    """
    Get all sellers
    """
    return SellerController.get_all_sellers()




@router.get("/{seller_uid}", response_model=SellerResponse)
def get_seller(seller_uid: str):
    """
    Get seller by UID
    """
    return SellerController.get_seller(seller_uid)


@router.patch("/{seller_uid}", response_model=SellerResponse)
def update_seller(seller_uid: str, seller_data: SellerUpdate):
    """
    Update seller information
    """
    return SellerController.update_seller(seller_uid, seller_data)


@router.delete("/{seller_uid}", status_code=status.HTTP_200_OK)
def delete_seller(seller_uid: str):
    """
    Delete seller
    """
    return SellerController.delete_seller(seller_uid)


@router.get("/{seller_uid}/rating")
def get_seller_rating(seller_uid: str):
    """
    Get seller rating summary (average rating and review count)
    """
    from ..models import Seller
    from ..utils.dependencies import _retry_get_or_none
    from fastapi import HTTPException
    
    # Check if seller exists
    seller = _retry_get_or_none(Seller, uid=seller_uid)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    
    # For now, return default rating (you can implement review system later)
    return {
        "seller_uid": seller_uid,
        "average_rating": 0.0,
        "review_count": 0,
        "name": seller.name,
        "location": seller.location
    }
