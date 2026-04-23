from .auth_routes import router as auth_router
from .user_routes import router as user_router
from .farm_product_routes import router as farm_product_router
from .order_routes import router as order_router
from .notification_routes import router as notification_router
from .message_routes import router as message_router
from .review_routes import router as review_router
from .cart_routes import router as cart_router
from .admin_routes import router as admin_router

__all__ = [
    "auth_router",
    "user_router",
    "farm_product_router",
    "order_router",
    "notification_router",
    "message_router",
    "review_router",
    "cart_router",
    "admin_router"
]
