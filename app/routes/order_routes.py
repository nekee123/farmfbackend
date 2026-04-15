from fastapi import APIRouter, status
from typing import List
from ..schemas import OrderCreate, OrderStatusUpdate, OrderResponse
from ..controllers import OrderController

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate):
    """
    Place a new order
    """
    return OrderController.create_order(order_data)


@router.get("/", response_model=List[OrderResponse])
def get_all_orders():
    """
    Get all orders (admin view)
    """
    return OrderController.get_all_orders()


@router.get("/buyer/{buyer_uid}", response_model=List[OrderResponse])
def get_buyer_orders(buyer_uid: str):
    """
    Get all orders for a buyer
    """
    return OrderController.get_buyer_orders(buyer_uid)


@router.get("/seller/{seller_uid}", response_model=List[OrderResponse])
def get_seller_orders(seller_uid: str):
    """
    Get all orders for a seller
    """
    return OrderController.get_seller_orders(seller_uid)


@router.get("/{order_uid}", response_model=OrderResponse)
def get_order(order_uid: str):
    """
    Get order by UID
    """
    return OrderController.get_order(order_uid)


@router.patch("/{order_uid}/status", status_code=status.HTTP_200_OK)
def update_order_status(order_uid: str, status_data: OrderStatusUpdate):
    """
    Update order status to Delivered only
    
    This endpoint only allows changing status to "Delivered".
    Prevents changing back to "Pending".
    """
    return OrderController.update_order_status(order_uid, status_data)


@router.delete("/{order_uid}", status_code=status.HTTP_200_OK)
def delete_order(order_uid: str):
    """
    Delete an order
    """
    return OrderController.delete_order(order_uid)
