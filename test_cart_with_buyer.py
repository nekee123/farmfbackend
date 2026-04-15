import requests
import json

BASE_URL = "http://localhost:8000"

def create_test_buyer():
    """Create a test buyer"""
    buyer_data = {
        "name": "Test Buyer",
        "phone_number": "+639123456789",
        "password": "password123",
        "location": "Test Location"
    }
    
    response = requests.post(f"{BASE_URL}/buyers/", json=buyer_data)
    if response.status_code == 201:
        buyer = response.json()
        print(f"✅ Buyer created: {buyer['uid']}")
        return buyer['uid']
    elif response.status_code == 400 and "already registered" in response.text:
        print("✅ Buyer already exists")
        return "test-buyer-uid"  # Use existing buyer UID
    else:
        print(f"❌ Failed to create buyer: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_cart():
    """Test cart functionality"""
    print("🛒 Testing Cart System")
    print("=" * 40)
    
    # Create test buyer
    buyer_uid = create_test_buyer()
    if not buyer_uid:
        return
    
    # Test add to cart
    print(f"\n1️⃣ Adding item to cart for buyer: {buyer_uid}")
    item_data = {
        "buyer_uid": buyer_uid,
        "product_uid": "6a6ab5c4276c45f29b6e9f064ccc78a3",
        "quantity": 2,
        "price_at_time": 25.0
    }
    
    response = requests.post(f"{BASE_URL}/cart/items", json=item_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        item = response.json()
        print(f"✅ Item added: {item['uid']}")
        print(f"   Product: {item['product_uid']}")
        print(f"   Quantity: {item['quantity']}")
        print(f"   Price: ₱{item['price_at_time']}")
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
    else:
        print(f"❌ Failed: {response.text}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_cart()
