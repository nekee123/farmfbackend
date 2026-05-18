from fastapi import APIRouter, Query, status, Depends
from typing import List, Optional
from ..schemas import FarmProductCreate, FarmProductUpdate, FarmProductResponse
from ..controllers import FarmProductController
from ..utils.dependencies import seller_only, seller_or_admin_only
from ..models.user import User

router = APIRouter(prefix="/api/products", tags=["Farm Products"])


@router.post("/", response_model=FarmProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_data: FarmProductCreate, current_user: User = Depends(seller_only)):
    """
    Create a new farm product (Sellers only)
    """
    return FarmProductController.create_product(product_data, current_user)


@router.get("/", response_model=List[FarmProductResponse])
def get_all_products(
    name: Optional[str] = Query(None, description="Search by product name"),
    type: Optional[str] = Query(None, description="Filter by farm product type"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    seller_uid: Optional[str] = Query(None, description="Filter by seller UID")
):
    """
    Get all farm products with optional filters
    """
    return FarmProductController.get_all_products(
        name=name,
        type=type,
        min_price=min_price,
        max_price=max_price,
        seller_uid=seller_uid
    )


@router.get("/{product_uid}", response_model=FarmProductResponse)
def get_product(product_uid: str):
    """
    Get farm product by UID
    """
    return FarmProductController.get_product(product_uid)


@router.patch("/{product_uid}", response_model=FarmProductResponse)
def update_product(
    product_uid: str,
    product_data: FarmProductUpdate,
    current_user: User = Depends(seller_or_admin_only)
):
    """
    Update farm product (Owner seller or Admin only)
    """
    return FarmProductController.update_product(product_uid, product_data, current_user)


@router.delete("/{product_uid}", status_code=status.HTTP_200_OK)
def delete_product(product_uid: str, current_user: User = Depends(seller_or_admin_only)):
    """
    Delete farm product (Owner seller or Admin only)
    """
    return FarmProductController.delete_product(product_uid, current_user)

