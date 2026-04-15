from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from ..database import get_db
import uuid

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

# Pydantic models
class NotificationCreate(BaseModel):
    recipient_uid: str
    recipient_type: str  # "buyer" or "seller"
    type: str  # order_approved, new_order, new_review, etc.
    message: str

class NotificationResponse(BaseModel):
    uid: str
    recipient_uid: str
    recipient_type: str
    type: str
    message: str
    read: bool
    created_at: str

# Get buyer notifications
@router.get("/buyer/{buyer_uid}", response_model=List[NotificationResponse])
def get_buyer_notifications(buyer_uid: str):
    """Get all notifications for a buyer"""
    driver = get_db()
    with driver.session() as session:
        query = """
        MATCH (n:Notification {recipient_uid: $buyer_uid, recipient_type: 'buyer'})
        RETURN n.uid AS uid, n.recipient_uid AS recipient_uid, 
               n.recipient_type AS recipient_type, n.type AS type,
               n.message AS message, n.read AS read, n.created_at AS created_at
        ORDER BY n.created_at DESC
        """
        result = session.run(query, {"buyer_uid": buyer_uid})
        notifications = []
        for record in result:
            notifications.append({
                "uid": record["uid"],
                "recipient_uid": record["recipient_uid"],
                "recipient_type": record["recipient_type"],
                "type": record["type"],
                "message": record["message"],
                "read": record["read"],
                "created_at": record["created_at"]
            })
        return notifications

# Get seller notifications
@router.get("/seller/{seller_uid}", response_model=List[NotificationResponse])
def get_seller_notifications(seller_uid: str):
    """Get all notifications for a seller"""
    driver = get_db()
    with driver.session() as session:
        query = """
        MATCH (n:Notification {recipient_uid: $seller_uid, recipient_type: 'seller'})
        RETURN n.uid AS uid, n.recipient_uid AS recipient_uid, 
               n.recipient_type AS recipient_type, n.type AS type,
               n.message AS message, n.read AS read, n.created_at AS created_at
        ORDER BY n.created_at DESC
        """
        result = session.run(query, {"seller_uid": seller_uid})
        notifications = []
        for record in result:
            notifications.append({
                "uid": record["uid"],
                "recipient_uid": record["recipient_uid"],
                "recipient_type": record["recipient_type"],
                "type": record["type"],
                "message": record["message"],
                "read": record["read"],
                "created_at": record["created_at"]
            })
        return notifications

# Create notification (internal use)
@router.post("/", response_model=NotificationResponse)
def create_notification(notification: NotificationCreate):
    """Create a new notification"""
    driver = get_db()
    with driver.session() as session:
        notif_uid = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        query = """
        CREATE (n:Notification {
            uid: $uid,
            recipient_uid: $recipient_uid,
            recipient_type: $recipient_type,
            type: $type,
            message: $message,
            read: false,
            created_at: $created_at
        })
        RETURN n.uid AS uid, n.recipient_uid AS recipient_uid,
               n.recipient_type AS recipient_type, n.type AS type,
               n.message AS message, n.read AS read, n.created_at AS created_at
        """
        
        result = session.run(query, {
            "uid": notif_uid,
            "recipient_uid": notification.recipient_uid,
            "recipient_type": notification.recipient_type,
            "type": notification.type,
            "message": notification.message,
            "created_at": created_at
        })
        
        record = result.single()
        return {
            "uid": record["uid"],
            "recipient_uid": record["recipient_uid"],
            "recipient_type": record["recipient_type"],
            "type": record["type"],
            "message": record["message"],
            "read": record["read"],
            "created_at": record["created_at"]
        }

# Mark notification as read
@router.patch("/{notification_uid}/read")
def mark_notification_read(notification_uid: str):
    """Mark a notification as read"""
    driver = get_db()
    with driver.session() as session:
        query = """
        MATCH (n:Notification {uid: $uid})
        SET n.read = true
        RETURN n.uid AS uid
        """
        result = session.run(query, {"uid": notification_uid})
        if not result.single():
            raise HTTPException(status_code=404, detail="Notification not found")
        return {"success": True, "message": "Notification marked as read"}

# Mark all buyer notifications as read
@router.patch("/buyer/{buyer_uid}/read-all")
def mark_all_buyer_notifications_read(buyer_uid: str):
    """Mark all buyer notifications as read"""
    driver = get_db()
    with driver.session() as session:
        query = """
        MATCH (n:Notification {recipient_uid: $buyer_uid, recipient_type: 'buyer'})
        SET n.read = true
        RETURN count(n) AS count
        """
        result = session.run(query, {"buyer_uid": buyer_uid})
        count = result.single()["count"]
        return {"success": True, "message": f"Marked {count} notifications as read"}

# Mark all seller notifications as read
@router.patch("/seller/{seller_uid}/read-all")
def mark_all_seller_notifications_read(seller_uid: str):
    """Mark all seller notifications as read"""
    driver = get_db()
    with driver.session() as session:
        query = """
        MATCH (n:Notification {recipient_uid: $seller_uid, recipient_type: 'seller'})
        SET n.read = true
        RETURN count(n) AS count
        """
        result = session.run(query, {"seller_uid": seller_uid})
        count = result.single()["count"]
        return {"success": True, "message": f"Marked {count} notifications as read"}

# Delete notification
@router.delete("/{notification_uid}")
def delete_notification(notification_uid: str):
    """Delete a notification"""
    driver = get_db()
    with driver.session() as session:
        query = """
        MATCH (n:Notification {uid: $uid})
        DELETE n
        RETURN count(n) AS deleted
        """
        result = session.run(query, {"uid": notification_uid})
        deleted = result.single()["deleted"]
        if deleted == 0:
            raise HTTPException(status_code=404, detail="Notification not found")
        return {"success": True, "message": "Notification deleted"}
