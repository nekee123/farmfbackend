from neomodel import (
    StructuredNode,
    StringProperty,
    UniqueIdProperty,
    DateTimeProperty,
    RelationshipFrom
)
from datetime import datetime


class Seller(StructuredNode):
    """Seller node in Neo4j graph database"""
    
    uid = UniqueIdProperty()
    name = StringProperty(required=True, index=True)
    phone_number = StringProperty(required=True, unique_index=True)
    location = StringProperty(default="")  # Seller's location
    password_hash = StringProperty(required=True)
    profile_picture = StringProperty(default="")  # Base64 encoded image
    
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty(default_now=True)
    
    # Relationships
    # Use fully-qualified paths to avoid neomodel resolving attributes on the wrong module
    farm_products = RelationshipFrom('app.models.farm_product.FarmProduct', 'SOLD_BY')
    orders = RelationshipFrom('app.models.order.Order', 'FULFILLED_BY')
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
        self.save()
