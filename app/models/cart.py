from neomodel import (
    StructuredNode,
    StringProperty,
    IntegerProperty,
    FloatProperty,
    DateTimeProperty,
    RelationshipTo,
    RelationshipFrom,
    UniqueIdProperty
)
from datetime import datetime
from .buyer import Buyer
from .farm_product import FarmProduct


class Cart(StructuredNode):
    """Cart node in Neo4j graph database"""
    
    uid = UniqueIdProperty()
    buyer_uid = StringProperty(required=True, index=True)
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty(default_now=True)
    
    # Relationships
    buyer = RelationshipTo('app.models.buyer.Buyer', 'OWNED_BY')
    cart_items = RelationshipTo('app.models.cart.CartItem', 'CONTAINS')
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
        self.save()


class CartItem(StructuredNode):
    """Cart Item node in Neo4j graph database"""

    uid = UniqueIdProperty()
    buyer_uid = StringProperty(index=True)  # Direct reference to buyer's UID
    product_uid = StringProperty(required=True, index=True)
    quantity = IntegerProperty(default=1)  # Can't have both required=True and default=1
    price_at_time = FloatProperty(required=True)  # Price when added to cart
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty(default_now=True)

    # Relationships
    cart = RelationshipTo('app.models.cart.Cart', 'IN_CART')
    product = RelationshipTo('app.models.farm_product.FarmProduct', 'IS_PRODUCT')
    
    def update_timestamp(self):
        """Update the timestamp"""
        self.updated_at = datetime.utcnow()
        self.save()
