from neomodel import StructuredNode, StringProperty, BooleanProperty, DateTimeProperty
from datetime import datetime


class Notification(StructuredNode):
    """
    Notification model for user notifications
    """
    uid = StringProperty(unique_index=True, required=True)
    recipient_uid = StringProperty(index=True, required=True)
    sender_name = StringProperty(required=True)
    product_name = StringProperty(required=True)
    type = StringProperty(required=True)  # "order_placed", "order_confirmed", "order_rejected"
    is_read = BooleanProperty(default=False)
    created_at = DateTimeProperty(default=datetime.utcnow)

    def update_timestamp(self):
        """Update the created_at timestamp"""
        self.created_at = datetime.utcnow()
        self.save()
