from neomodel import (
    StructuredNode,
    StringProperty,
    UniqueIdProperty,
    DateTimeProperty,
    BooleanProperty,
    RelationshipFrom,
    RelationshipTo
)
from datetime import datetime
from enum import Enum


class AdminRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    MODERATOR = "moderator"
    SUPPORT = "support"


class Admin(StructuredNode):
    """Admin node in Neo4j graph database"""
    
    uid = UniqueIdProperty()
    username = StringProperty(required=True, unique_index=True)
    email = StringProperty(required=True, unique_index=True)
    full_name = StringProperty(required=True)
    password_hash = StringProperty(required=True)
    role = StringProperty(default=AdminRole.MODERATOR.value)
    is_active = BooleanProperty(default=True)
    permissions = StringProperty(default="")  # JSON string of permissions
    
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty(default_now=True)
    last_login = DateTimeProperty(default=None)
    
    # Relationships
    # Admin can manage users
    managed_buyers = RelationshipTo('app.models.buyer.Buyer', 'MANAGED_BY')
    managed_sellers = RelationshipTo('app.models.seller.Seller', 'MANAGED_BY')
    # Admin can moderate products
    moderated_products = RelationshipTo('app.models.farm_product.FarmProduct', 'MODERATED_BY')
    # Admin can handle orders
    managed_orders = RelationshipTo('app.models.order.Order', 'MANAGED_BY')
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
        self.save()
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.utcnow()
        self.save()
    
    def has_permission(self, permission: str) -> bool:
        """Check if admin has specific permission"""
        if self.role == AdminRole.SUPER_ADMIN.value:
            return True
        
        # Parse permissions JSON string
        try:
            import json
            permissions = json.loads(self.permissions) if self.permissions else []
            return permission in permissions
        except:
            return False
    
    def get_permissions_list(self) -> list:
        """Get list of permissions as Python list"""
        try:
            import json
            return json.loads(self.permissions) if self.permissions else []
        except:
            return []


class AdminActivity(StructuredNode):
    """Track admin activities for audit purposes"""
    
    uid = UniqueIdProperty()
    admin_uid = StringProperty(required=True, index=True)
    action = StringProperty(required=True)
    target_type = StringProperty(required=True)  # 'user', 'product', 'order'
    target_uid = StringProperty(required=True)
    description = StringProperty()
    ip_address = StringProperty()
    user_agent = StringProperty()
    
    created_at = DateTimeProperty(default_now=True)
    
    # Relationship back to admin
    performed_by = RelationshipFrom(Admin, 'PERFORMED')
