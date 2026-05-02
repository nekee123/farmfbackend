from neomodel import (

    StructuredNode,

    StringProperty,

    UniqueIdProperty,

    DateTimeProperty,

    RelationshipFrom

)

from datetime import datetime





class Buyer(StructuredNode):

    """Buyer node in Neo4j graph database"""

    

    uid = UniqueIdProperty()

    full_name = StringProperty(required=True, index=True)

    phone_number = StringProperty(required=True, unique_index=True)

    location = StringProperty(default="")

    password_hash = StringProperty(required=True)

    profile_picture = StringProperty(default="")  # Base64 encoded image

    

    created_at = DateTimeProperty(default_now=True)

    updated_at = DateTimeProperty(default_now=True)

    

    # Relationships

    # Use fully-qualified path to avoid neomodel attribute lookup issues

    orders = RelationshipFrom('app.models.order.Order', 'PLACED_BY')

    

    def update_timestamp(self):

        """Update the updated_at timestamp"""

        self.updated_at = datetime.utcnow()

        self.save()

