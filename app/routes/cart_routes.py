from fastapi import APIRouter, status, HTTPException
from typing import List, Optional
from ..schemas import CartItemCreate, CartItemUpdate, CartResponse, CartItemResponse, CartSummary
from ..controllers import CartController

router = APIRouter(prefix="/api/cart", tags=["Cart"])


@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(item_data: CartItemCreate):
    """
    Add item to cart
    """
    return CartController.add_item_to_cart(item_data.buyer_uid, item_data)


@router.get("/", response_model=CartResponse)
def get_cart(buyer_uid: Optional[str] = None):
    """
    Get cart with all items
    """
    if not buyer_uid:
        raise HTTPException(status_code=400, detail="buyer_uid query parameter is required")
    return CartController.get_cart(buyer_uid)


@router.get("/summary", response_model=CartSummary)
def get_cart_summary(buyer_uid: Optional[str] = None):
    """
    Get cart summary (item count and total amount)
    """
    if not buyer_uid:
        raise HTTPException(status_code=400, detail="buyer_uid query parameter is required")
    return CartController.get_cart_summary(buyer_uid)


@router.put("/items/{item_uid}", response_model=CartItemResponse)
def update_cart_item(item_uid: str, item_data: CartItemUpdate, buyer_uid: Optional[str] = None):
    """
    Update cart item quantity
    """
    if not buyer_uid:
        raise HTTPException(status_code=400, detail="buyer_uid query parameter is required")
    return CartController.update_cart_item(buyer_uid, item_uid, item_data)


@router.delete("/items/{item_uid}", status_code=status.HTTP_200_OK)
def remove_from_cart(item_uid: str, buyer_uid: Optional[str] = None):
    """
    Remove item from cart
    """
    if not buyer_uid:
        raise HTTPException(status_code=400, detail="buyer_uid query parameter is required")
    return CartController.remove_from_cart(buyer_uid, item_uid)


@router.delete("/", status_code=status.HTTP_200_OK)
def clear_cart(buyer_uid: Optional[str] = None):
    """
    Clear all items from cart
    """
    if not buyer_uid:
        raise HTTPException(status_code=400, detail="buyer_uid query parameter is required")
    return CartController.clear_cart(buyer_uid)
