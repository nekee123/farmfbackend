from fastapi import APIRouter, status, Depends
from typing import List
from ..schemas import NotificationCreate, NotificationResponse
from ..controllers import NotificationController
from ..utils.dependencies import get_current_user
from ..models.user import User
from ..database import get_db
from ..controllers.order_controller import create_favorite, get_favorite_products, remove_favorite
router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(notification_data: NotificationCreate):
    """
    Create a new notification (internal use)
    """
    return NotificationController.create_notification(notification_data)


@router.get("/", response_model=List[dict])
def get_notifications(current_user: User = Depends(get_current_user)):
    """
    Get all notifications for the current user
    """
    return NotificationController.get_user_notifications(current_user.uid)


@router.put("/{notification_uid}/read", status_code=status.HTTP_200_OK)
def mark_notification_as_read(notification_uid: str, current_user: User = Depends(get_current_user)):
    """
    Mark a notification as read
    """
    return NotificationController.mark_as_read(notification_uid, current_user.uid)


@router.get("/unread-count", status_code=status.HTTP_200_OK)
def get_unread_count(current_user: User = Depends(get_current_user)):
    """
    Get unread notification count for current user
    """
    driver = get_db()
    with driver.session() as session:
        query = """
        MATCH (n:Notification {recipient_uid: $recipient_uid})
        WHERE NOT n.is_read
        RETURN count(n) AS unread_count
        """
        result = session.run(query, {"recipient_uid": current_user.uid})
        record = result.single()
        return {
            "unread_count": record["unread_count"] if record else 0
        }

@router.get("/get_favorites")
def get_favorites(current_user: User = Depends(get_current_user)):
    print("i reach the routes")
    return get_favorite_products(current_user.uid)