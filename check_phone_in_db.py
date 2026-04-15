from neomodel import db
from app.models import Buyer

print("Checking for buyer with phone 09123456789...")

try:
    # Direct database query
    query = """
    MATCH (b:Buyer)
    WHERE b.phone_number = '09123456789'
    RETURN b.uid AS uid, b.name AS name, b.phone_number AS phone_number,
           b.created_at AS created_at, b.updated_at AS updated_at
    """
    
    results, meta = db.cypher_query(query)
    
    if results:
        print("Found existing buyer:")
        for row in results:
            print(f"  UID: {row[0]}")
            print(f"  Name: {row[1]}")
            print(f"  Phone: {row[2]}")
            print(f"  Created: {row[3]}")
            print(f"  Updated: {row[4]}")
    else:
        print("No buyer found with that phone number")
        
except Exception as e:
    print(f"Error: {e}")

print("\nTrying to find the buyer using neomodel...")

try:
    buyer = Buyer.nodes.get_or_none(phone_number='09123456789')
    if buyer:
        print(f"Found buyer: {buyer.name} (UID: {buyer.uid})")
    else:
        print("Buyer not found")
except Exception as e:
    print(f"Error: {e}")
