from neomodel import (
    StructuredNode,
    StringProperty,
    UniqueIdProperty,
    DateTimeProperty,
    RelationshipTo,
    RelationshipFrom,
    BooleanProperty
)
from datetime import datetime
from enum import Enum
from neomodel import ArrayProperty, StringProperty


class UserRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"


class User(StructuredNode):
    """Unified User node for buyers, sellers, and admins"""
    
    uid = UniqueIdProperty()
    phone_number = StringProperty(required=True, unique_index=True)
    password_hash = StringProperty(required=True)
    full_name = StringProperty(required=True)
    role = StringProperty(default=UserRole.BUYER.value, index=True)
    location = StringProperty(default="")
    profile_picture = StringProperty(default="")
    category = ArrayProperty(StringProperty(), default=[])
    is_banned = BooleanProperty(default=False)
    is_verified = BooleanProperty(default=False)
    otp_code = StringProperty(default="")
    otp_expiry = DateTimeProperty(default=None)
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty(default_now=True)
    last_login = DateTimeProperty(default=None)

    # Relationships
    # For Buyers
    orders_placed = RelationshipFrom('app.models.order.Order', 'PLACED_BY')
    
    # For Sellers
    products_sold = RelationshipFrom('app.models.farm_product.FarmProduct', 'SOLD_BY')
    orders_fulfilled = RelationshipFrom('app.models.order.Order', 'FULFILLED_BY')
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
        self.save()

    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.utcnow()
        self.save()
