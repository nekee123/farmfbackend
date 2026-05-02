from fastapi import APIRouter, status, Depends
from typing import List
from ..schemas import MessageCreate, MessageResponse
from ..controllers import MessageController
from ..utils.dependencies import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/messages", tags=["Messages"])


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(message_data: MessageCreate):
    """
    Create a new message
    """
    return MessageController.create_message(message_data)


@router.get("/conversations", response_model=List[dict])
def get_conversations(current_user: User = Depends(get_current_user)):
    """
    Get list of all conversations for current user with unread message count
    """
    return MessageController.get_conversations(current_user.uid)


@router.get("/{user_uid}", response_model=List[dict])
def get_messages(user_uid: str, current_user: User = Depends(get_current_user)):
    """
    Get all messages between current user and specified user
    """
    return MessageController.get_messages(current_user.uid, user_uid)


@router.put("/{message_uid}/read", status_code=status.HTTP_200_OK)
def mark_message_as_read(message_uid: str, current_user: User = Depends(get_current_user)):
    """
    Mark a message as read
    """
    return MessageController.mark_as_read(message_uid, current_user.uid)

@router.get("/chat/messages")
def get_messages(user1: str, user2: str):
    query = """
    MATCH (m:Message)
    WHERE 
        (m.sender_uid = $user1 AND m.receiver_uid = $user2)
        OR
        (m.sender_uid = $user2 AND m.receiver_uid = $user1)
    RETURN m
    ORDER BY m.timestamp ASC
    """

    # run query

    return {"messages": []}