from typing import List
from fastapi import HTTPException, status
from ..models import Notification
from ..schemas import NotificationCreate, NotificationResponse
from ..database import get_db
from datetime import datetime
import uuid


class NotificationController:
    """Controller for Notification CRUD operations"""
    
    @staticmethod
    def create_notification(notification_data: NotificationCreate) -> dict:
        """Create a new notification"""
        notif_uid = str(uuid.uuid4())
        notification = Notification(
            uid=notif_uid,
            recipient_uid=notification_data.recipient_uid,
            sender_name=notification_data.sender_name,
            product_name=notification_data.product_name,
            type=notification_data.type,
            is_read=False,
            created_at=datetime.utcnow()
        ).save()
        
        return NotificationController._to_response(notification)
    
    @staticmethod
    def get_user_notifications(recipient_uid: str) -> List[dict]:
        """Get all notifications for a specific user"""
        driver = get_db()
        with driver.session() as session:
            query = """
            MATCH (n:Notification {recipient_uid: $recipient_uid})
            RETURN n.uid as uid, n.recipient_uid as recipient_uid, n.sender_name as sender_name,
                   n.product_name as product_name, n.type as type, n.is_read as is_read,
                   n.created_at as created_at
            ORDER BY n.created_at DESC
            """
            
            results = session.run(query, {"recipient_uid": recipient_uid})
            
            notifications = []
            for record in results:
                notifications.append({
                    "uid": record["uid"],
                    "recipient_uid": record["recipient_uid"],
                    "sender_name": record["sender_name"],
                    "product_name": record["product_name"],
                    "type": record["type"],
                    "is_read": record["is_read"],
                    "created_at": record["created_at"]
                })
            
            return notifications
    
    @staticmethod
    def mark_as_read(notification_uid: str, recipient_uid: str) -> dict:
        """Mark a notification as read"""
        notification = Notification.nodes.get_or_none(uid=notification_uid)
        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        
        # Verify the notification belongs to the user
        if notification.recipient_uid != recipient_uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only mark your own notifications as read"
            )
        
        notification.is_read = True
        notification.save()
        
        return NotificationController._to_response(notification)
    
    @staticmethod
    def _to_response(notification: Notification) -> dict:
        """Convert Notification model to response dictionary"""
        return {
            "uid": notification.uid,
            "recipient_uid": notification.recipient_uid,
            "sender_name": notification.sender_name,
            "product_name": notification.product_name,
            "type": notification.type,
            "is_read": notification.is_read,
            "created_at": notification.created_at
        }
