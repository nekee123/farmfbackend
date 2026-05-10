from neomodel import (
    StructuredNode,
    StringProperty,
    UniqueIdProperty,
    DateTimeProperty,
    FloatProperty,
    IntegerProperty,
    RelationshipTo
)
from datetime import datetime


class Order(StructuredNode):
    """Order node in Neo4j graph database"""

    uid = UniqueIdProperty()
    buyer_uid = StringProperty(index=True)  # Direct reference to buyer's UID
    seller_uid = StringProperty(index=True)  # Direct reference to seller's UID
    quantity = IntegerProperty(default=1)
    total_price = FloatProperty(required=True)
    buyer_address = StringProperty(required=True)
    order_status = StringProperty(
        default="Pending",
        choices={
            "Pending": "Pending",
            "Confirmed": "Confirmed",
            "Cancelled": "Cancelled",
            "Delivered": "Delivered"
        }
    )

    payment_method = StringProperty(choices={
        "CASH_ON_DELIVERY": "Cash on Delivery",
        "MEET_UP_CASH_ON_PICKUP": "Meet Up / Cash on Pick-up"
    }, required=True)

    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty(default_now=True)
    
    # Relationships
    buyer = RelationshipTo('app.models.user.User', 'PLACED_BY')
    seller = RelationshipTo('app.models.user.User', 'FULFILLED_BY')
    farm_product = RelationshipTo('app.models.farm_product.FarmProduct', 'CONTAINS')
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
        self.save()
