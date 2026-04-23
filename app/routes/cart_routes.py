from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Optional
from ..schemas import CartItemCreate, CartItemUpdate, CartResponse, CartItemResponse, CartSummary
from ..controllers import CartController
from ..utils.dependencies import buyer_only
from ..models.user import User

router = APIRouter(prefix="/api/cart", tags=["Cart"])


@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(item_data: CartItemCreate, current_user: User = Depends(buyer_only)):
    """
    Add item to cart (Buyer only)
    """
    return CartController.add_item_to_cart(current_user.uid, item_data)


@router.get("/", response_model=CartResponse)
def get_cart(current_user: User = Depends(buyer_only)):
    """
    Get cart with all items (Buyer only)
    """
    return CartController.get_cart(current_user.uid)


@router.get("/summary", response_model=CartSummary)
def get_cart_summary(current_user: User = Depends(buyer_only)):
    """
    Get cart summary (item count and total amount) (Buyer only)
    """
    return CartController.get_cart_summary(current_user.uid)


@router.put("/items/{item_uid}", response_model=CartItemResponse)
def update_cart_item(item_uid: str, item_data: CartItemUpdate, current_user: User = Depends(buyer_only)):
    """
    Update cart item quantity (Buyer only)
    """
    return CartController.update_cart_item(current_user.uid, item_uid, item_data)


@router.delete("/items/{item_uid}", status_code=status.HTTP_200_OK)
def remove_from_cart(item_uid: str, current_user: User = Depends(buyer_only)):
    """
    Remove item from cart (Buyer only)
    """
    return CartController.remove_from_cart(current_user.uid, item_uid)


@router.delete("/", status_code=status.HTTP_200_OK)
def clear_cart(current_user: User = Depends(buyer_only)):
    """
    Clear all items from cart (Buyer only)
    """
    return CartController.clear_cart(current_user.uid)
