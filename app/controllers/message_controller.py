from typing import List
from fastapi import HTTPException, status
from ..models import Message, User
from ..schemas import MessageCreate, MessageResponse, ConversationResponse
from ..database import get_db
from datetime import datetime
import uuid

from typing import List
from fastapi import HTTPException, status
from ..models import Message, User
from ..schemas import MessageCreate, MessageResponse, ConversationResponse
from ..database import get_db
from datetime import datetime
import uuid
from neo4j.time import DateTime as Neo4jDateTime   # 👈 add this too


# =========================
# UTIL FUNCTION (PUT HERE)
# =========================
def normalize_datetime(value):
    if value is None:
        return None

    if isinstance(value, Neo4jDateTime):
        return value.iso_format()

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, (float, int)):
        return datetime.utcfromtimestamp(value).isoformat()

    return str(value)


class MessageController:
    """Controller for Message operations"""
    
    @staticmethod
    def create_message(message_data: MessageCreate) -> dict:
        """Create a new message"""
        message_uid = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Verify both users exist
        driver = get_db()
        with driver.session() as session:
            sender_check = session.run(
                "MATCH (u:User {uid: $uid}) RETURN u.uid",
                {"uid": message_data.sender_uid}
            )
            if not sender_check.single():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sender not found")
            
            receiver_check = session.run(
                "MATCH (u:User {uid: $uid}) RETURN u.uid",
                {"uid": message_data.receiver_uid}
            )
            if not receiver_check.single():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver not found")
        
        # Create message node
        message = Message(
            uid=message_uid,
            sender_uid=message_data.sender_uid,
            receiver_uid=message_data.receiver_uid,
            message=message_data.message,
            is_read=False,
            created_at=now,
            updated_at=now
        ).save()
        
        return MessageController._to_response(message)
    
    @staticmethod
    def get_messages(current_user_uid: str, other_user_uid: str) -> List[dict]:
        """Get all messages between current user and specified user"""
        driver = get_db()
        with driver.session() as session:
            query = """
            MATCH (m:Message)
            WHERE (m.sender_uid = $current_uid AND m.receiver_uid = $other_uid)
               OR (m.sender_uid = $other_uid AND m.receiver_uid = $current_uid)
            RETURN m.uid AS uid, m.sender_uid AS sender_uid, m.receiver_uid AS receiver_uid,
                   m.message AS message, m.is_read AS is_read,
                   m.created_at AS created_at, m.updated_at AS updated_at
            ORDER BY m.created_at ASC
            """
            
            results = session.run(query, {
                "current_uid": current_user_uid,
                "other_uid": other_user_uid
            })
            
            messages = []
            for record in results:
                messages.append({
                    "uid": record["uid"],
                    "sender_uid": record["sender_uid"],
                    "receiver_uid": record["receiver_uid"],
                    "message": record["message"],
                    "is_read": record["is_read"],
                    "created_at": normalize_datetime(record["created_at"]),
                    "updated_at": normalize_datetime(record["updated_at"])  
                })     
            return messages
    
    @staticmethod
    def mark_as_read(message_uid: str, current_user_uid: str) -> dict:
        """Mark a message as read"""
        driver = get_db()
        with driver.session() as session:
            # Verify message exists and belongs to current user as receiver
            query = """
            MATCH (m:Message {uid: $uid})
            WHERE m.receiver_uid = $current_uid
            RETURN m.uid AS uid
            """
            result = session.run(query, {"uid": message_uid, "current_uid": current_user_uid})
            if not result.single():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found or you are not the receiver")
            
            # Mark as read
            update_query = """
            MATCH (m:Message {uid: $uid})
            SET m.is_read = true, m.updated_at = $updated_at
            RETURN m.uid AS uid, m.sender_uid AS sender_uid, m.receiver_uid AS receiver_uid,
                   m.message AS message, m.is_read AS is_read,
                   m.created_at AS created_at, m.updated_at AS updated_at
            """
            result = session.run(update_query, {
                "uid": message_uid,
                "updated_at": datetime.utcnow()
            })
            
            record = result.single()
            return {
                "uid": record["uid"],
                "sender_uid": record["sender_uid"],
                "receiver_uid": record["receiver_uid"],
                "message": record["message"],
                "is_read": record["is_read"],
                "created_at": record["created_at"],
                "updated_at": record["updated_at"]
            }
    
    @staticmethod
    def get_conversations(current_user_uid: str) -> List[dict]:
        """Get list of all conversations for current user with unread message count"""
        driver = get_db()

        with driver.session() as session:
            query = """
            MATCH (m:Message)
            WHERE m.sender_uid = $current_uid OR m.receiver_uid = $current_uid

            WITH 
                CASE 
                    WHEN m.sender_uid = $current_uid THEN m.receiver_uid
                    ELSE m.sender_uid
                END AS other_user_uid,
                m

            MATCH (u:User {uid: other_user_uid})

            WITH 
                other_user_uid,
                u.full_name AS user_name,
                u.profile_picture AS profile_picture,
                u.phone_number AS phone_number,
                m

            WITH 
                other_user_uid,
                user_name,
                profile_picture,
                phone_number,
                collect(m) AS messages

            WITH 
                other_user_uid,
                user_name,
                profile_picture,
                phone_number,
                messages,
                [msg IN messages WHERE msg.receiver_uid = $current_uid AND NOT msg.is_read] AS unread_messages,
                messages[-1] AS last_message

            RETURN 
                other_user_uid AS user_uid,
                user_name,
                profile_picture,
                phone_number,
                size(unread_messages) AS unread_count,
                last_message.message AS last_message,
                last_message.created_at AS last_message_time,
                false AS is_online

            ORDER BY last_message_time DESC
            """

            results = session.run(query, {"current_uid": current_user_uid})

            conversations = []

            for record in results:
                conversations.append({
                    "user_uid": record["user_uid"],
                    "user_name": record["user_name"],
                    "profile_picture": record.get("profile_picture"),
                    "phone_number": record.get("phone_number"),
                    "unread_count": record["unread_count"],
                    "last_message": record.get("last_message"),
                    "last_message_time": record.get("last_message_time"),
                    "is_online": record.get("is_online", False)
                })

            return conversations
    
    @staticmethod
    def _to_response(message: Message) -> dict:
        """Convert Message model to response dictionary"""
        return {
            "uid": message.uid,
            "sender_uid": message.sender_uid,
            "receiver_uid": message.receiver_uid,
            "message": message.message,
            "is_read": message.is_read,
            "created_at": message.created_at,
            "updated_at": message.updated_at
        }
