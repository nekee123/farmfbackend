from neomodel import StructuredNode, StringProperty, DateTimeProperty, BooleanProperty
from datetime import datetime


class Message(StructuredNode):
    """
    Message model for chat system
    """
    uid = StringProperty(unique_index=True, required=True)
    sender_uid = StringProperty(index=True, required=True)
    receiver_uid = StringProperty(index=True, required=True)
    message = StringProperty(required=True)
    is_read = BooleanProperty(default=False)
    created_at = DateTimeProperty(default=datetime.utcnow)
    updated_at = DateTimeProperty(default=datetime.utcnow)

    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
        self.save()
