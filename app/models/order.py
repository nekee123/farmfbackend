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
    quantity = IntegerProperty(default=1)
    total_price = FloatProperty(required=True)
    order_status = StringProperty(
        default="Pending",
        choices={
            "Pending": "Pending",
            "Confirmed": "Confirmed",
            "Cancelled": "Cancelled",
            "Delivered": "Delivered"
        }
    )
    
    payment_method = StringProperty(
        required=True,
        choices={
            "Cash on Delivery": "Cash on Delivery",
            "Meet Up / Cash on Pick-up": "Meet Up / Cash on Pick-up"
        }
    )
    
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty(default_now=True)
    
    # Relationships
    buyer = RelationshipTo('app.models.buyer.Buyer', 'PLACED_BY')
    seller = RelationshipTo('app.models.seller.Seller', 'FULFILLED_BY')
    farm_product = RelationshipTo('app.models.farm_product.FarmProduct', 'CONTAINS')
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
        self.save()
