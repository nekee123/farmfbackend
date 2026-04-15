import requests
import json

BASE_URL = "http://localhost:8000"

def test_cart():
    """Test cart functionality with existing buyer"""
    print("🛒 Testing Cart System")
    print("=" * 40)
    
    # Use existing buyer UID from previous test
    buyer_uid = "938aad84601c4b88b1bbc7a836e3da01"
    
    # Test add to cart
    print(f"\n1️⃣ Adding item to cart for buyer: {buyer_uid}")
    item_data = {
        "buyer_uid": buyer_uid,
        "product_uid": "aced98156e7e4ad69e510387a6acf6d8",  # Use the Buwahan product
        "quantity": 2,
        "price_at_time": 50.0
    }
    
    response = requests.post(f"{BASE_URL}/cart/items", json=item_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        item = response.json()
        print(f"✅ Item added: {item['uid']}")
        print(f"   Product: {item['product_uid']}")
        print(f"   Quantity: {item['quantity']}")
        print(f"   Price: ₱{item['price_at_time']}")
        if item.get('product'):
            print(f"   Product Name: {item['product']['name']}")
            print(f"   Product Type: {item['product']['type']}")
    else:
        print(f"❌ Failed: {response.text}")
        return
    
    # Test get cart
    print(f"\n2️⃣ Getting cart for buyer: {buyer_uid}")
    response = requests.get(f"{BASE_URL}/cart/?buyer_uid={buyer_uid}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        cart = response.json()
        print(f"✅ Cart loaded:")
        print(f"   Items: {len(cart['items'])}")
        print(f"   Total: ₱{cart['total_amount']}")
        
        # Show product details for each item
        for item in cart['items']:
            if item.get('product'):
                print(f"   - {item['product']['name']} ({item['quantity']}x) ₱{item['price_at_time']}")
            else:
                print(f"   - Unknown Product ({item['quantity']}x) ₱{item['price_at_time']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_cart()
