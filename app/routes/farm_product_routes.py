from fastapi import APIRouter, Query, status
from typing import List, Optional
from ..schemas import FarmProductCreate, FarmProductUpdate, FarmProductResponse
from ..controllers import FarmProductController

router = APIRouter(prefix="/api/products", tags=["Farm Products"])


@router.post("/", response_model=FarmProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_data: FarmProductCreate):
    """
    Create a new farm product
    """
    return FarmProductController.create_product(product_data)


@router.get("/", response_model=List[FarmProductResponse])
def get_all_products(
    name: Optional[str] = Query(None, description="Search by product name"),
    type: Optional[str] = Query(None, description="Filter by farm product type"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    seller_uid: Optional[str] = Query(None, description="Filter by seller UID")
):
    """
    Get all farm products with optional filters:
    - Search by name
    - Filter by type
    - Filter by price range
    - Filter by seller
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
def update_product(product_uid: str, product_data: FarmProductUpdate):
    """
    Update farm product
    """
    return FarmProductController.update_product(product_uid, product_data)


@router.delete("/{product_uid}", status_code=status.HTTP_200_OK)
def delete_product(product_uid: str):
    """
    Delete farm product
    """
    return FarmProductController.delete_product(product_uid)
