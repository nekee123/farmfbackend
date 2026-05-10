from fastapi import APIRouter, status, Depends
from typing import List
from ..schemas import OrderCreate, OrderStatusUpdate, OrderResponse
from ..controllers import OrderController
from ..utils.dependencies import buyer_only, seller_only, admin_only, get_current_user
from ..models.user import User
from fastapi import HTTPException
from ..controllers.order_controller import create_favorite, get_favorite_products, remove_favorite, is_favorited
router = APIRouter(prefix="/api/orders", tags=["Orders"])


import traceback

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_order(order_data: OrderCreate, current_user: User = Depends(buyer_only)):
    try:
        order = OrderController.create_order(order_data, current_user)
        return {
            "success": True,
            "error": None,
            "data": order
        }
    except Exception as e:
        import traceback
        traceback.print_exc()

        error_message = str(e)

    # 🔥 Handle FastAPI HTTPException properly
        if isinstance(e, HTTPException):
            error_message = e.detail

        return {
            "success": False,
            "error": error_message,
            "data": None
        }


@router.get("/", response_model=List[dict])
def get_all_orders(current_user: User = Depends(admin_only)):
    """
    Get all orders (Admin only)
    """
    return OrderController.get_all_orders()


@router.get("/my-orders", response_model=List[dict])
def get_my_orders(current_user: User = Depends(get_current_user)):
    """
    Get orders for current user (Buyers see their orders, Sellers see orders they fulfilled)
    """
    if current_user.role == "buyer":
        return OrderController.get_buyer_orders(current_user.uid)
    elif current_user.role == "seller":
        return OrderController.get_seller_orders(current_user.uid)
    else:
        return []


@router.get("/buyer/{buyer_id}", response_model=List[dict])
def get_buyer_orders_by_id(buyer_id: str, current_user: User = Depends(get_current_user)):
    """
    Get orders for a specific buyer (Admin can view all, buyers can only view their own)
    """
    # Only admin or the buyer themselves can view these orders
    if current_user.role != "admin" and current_user.uid != buyer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own orders"
        )
    return OrderController.get_buyer_orders(buyer_id)


@router.get("/seller/{seller_id}", response_model=List[dict])
def get_seller_orders_by_id(seller_id: str, current_user: User = Depends(get_current_user)):
    """
    Get orders for a specific seller (Admin can view all, sellers can only view their own)
    """
    # Only admin or the seller themselves can view these orders
    if current_user.role != "admin" and current_user.uid != seller_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own orders"
        )
    return OrderController.get_seller_orders(seller_id)


@router.get("/{order_uid}", response_model=dict)
def get_order(order_uid: str, current_user: User = Depends(get_current_user)):
    """
    Get order by UID
    """
    return OrderController.get_order(order_uid)


@router.patch("/{order_uid}/status", status_code=status.HTTP_200_OK)
def update_order_status(
    order_uid: str,
    status_data: OrderStatusUpdate,
    current_user: User = Depends(seller_only)
):
    """
    Update order status (Sellers only)
    """
    return OrderController.update_order_status(order_uid, status_data)


@router.put("/{order_uid}/cancel", status_code=status.HTTP_200_OK)
def cancel_order(order_uid: str, current_user: User = Depends(buyer_only)):
    """
    Cancel an order (Buyers only - can only cancel their own pending orders)
    """
    return OrderController.cancel_order(order_uid, current_user.uid)


@router.put("/{order_uid}/confirm", status_code=status.HTTP_200_OK)
def confirm_order(order_uid: str, current_user: User = Depends(seller_only)):
    """
    Confirm an order (Sellers only - can only confirm orders they are fulfilling)
    """
    return OrderController.confirm_order(order_uid, current_user.uid)


@router.put("/{order_uid}/reject", status_code=status.HTTP_200_OK)
def reject_order(order_uid: str, current_user: User = Depends(seller_only)):
    """
    Reject an order (Sellers only - can only reject orders they are fulfilling)
    """
    return OrderController.reject_order(order_uid, current_user.uid)


@router.put("/{order_uid}/delivered", status_code=status.HTTP_200_OK)
def mark_order_delivered(order_uid: str, current_user: User = Depends(seller_only)):
    """
    Mark an order as delivered (Sellers only - can only mark their own orders as delivered)
    """
    return OrderController.mark_order_delivered(order_uid, current_user.uid)


@router.delete("/{order_uid}", status_code=status.HTTP_200_OK)
def delete_order(order_uid: str, current_user: User = Depends(get_current_user)):
    """
    Delete an order (Admin can delete all, Sellers can delete their own cancelled/rejected orders)
    """
    if current_user.role == "admin":
        return OrderController.delete_order(order_uid)
    elif current_user.role == "seller":
        return OrderController.delete_order(order_uid, seller_uid=current_user.uid)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and sellers can delete orders"
        )


@router.post("/favorite/{product_uid}")
def favorite_product(product_uid: str, current_user: User = Depends(get_current_user)):
    create_favorite(current_user.uid, product_uid)
    print("i reach the post routes")
    return {"success": True, "message": "Added to favorites"}


@router.delete("/favorite/{product_uid}")
def unfavorite_product(product_uid: str, current_user: User = Depends(get_current_user)):
    remove_favorite(current_user.uid, product_uid)
    return {"success": True, "message": "Removed from favorites"}


@router.get("/favorite/check/{product_uid}")
def check_favorite(product_uid: str, current_user: User = Depends(get_current_user)):
    return {
        "is_favorited": is_favorited(current_user.uid, product_uid)
    }