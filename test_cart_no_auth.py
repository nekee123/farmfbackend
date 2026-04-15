import requests
import json

BASE_URL = "http://localhost:8000"

def test_cart_with_buyer_uid():
    """Test cart with buyer_uid in request body"""
    
    print("🛒 Testing Cart with Buyer UID")
    print("=" * 50)
    
    # Test 1: Add item to cart
    print("\n1️⃣ Adding item to cart...")
    item_data = {
        "buyer_uid": "12345",
        "product_uid": "57784e4eae96402fbb73f686678a1e56",
        "quantity": 1,
        "price_at_time": 19.99
    }
    
    response = requests.post(f"{BASE_URL}/cart/items", json=item_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        item = response.json()
        print(f"✅ Item added: {item['uid']}")
        print(f"   Buyer UID: {item_data['buyer_uid']}")
        print(f"   Product: {item_data['product_uid']}")
        print(f"   Quantity: {item_data['quantity']}")
        print(f"   Price: ₱{item_data['price_at_time']}")
    else:
        print(f"❌ Failed: {response.text}")
        return
    
    # Test 2: Get cart
    print("\n2️⃣ Getting cart...")
    response = requests.get(f"{BASE_URL}/cart/?buyer_uid=12345")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        cart = response.json()
        print(f"✅ Cart loaded:")
        print(f"   Items: {len(cart['items'])}")
        print(f"   Total: ₱{cart['total_amount']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 3: Get cart summary
    print("\n3️⃣ Getting cart summary...")
    response = requests.get(f"{BASE_URL}/cart/summary?buyer_uid=12345")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        summary = response.json()
        print(f"✅ Summary:")
        print(f"   Total items: {summary['total_items']}")
        print(f"   Items count: {summary['items_count']}")
        print(f"   Total amount: ₱{summary['total_amount']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    print("\n🎉 Test completed!")

def test_more_items():
    """Add multiple items to cart"""
    print("\n🛒 Adding Multiple Items")
    print("=" * 30)
    
    items = [
        {
            "buyer_uid": "12345",
            "product_uid": "57784e4eae96402fbb73f686678a1e56",
            "quantity": 2,
            "price_at_time": 19.99
        },
        {
            "buyer_uid": "12345",
            "product_uid": "6a6ab5c4276c45f29b6e9f064ccc78a3",
            "quantity": 3,
            "price_at_time": 25.00
        }
    ]
    
    for i, item in enumerate(items, 1):
        print(f"\nAdding item {i}...")
        response = requests.post(f"{BASE_URL}/cart/items", json=item)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Added: {result['uid']}")
        else:
            print(f"❌ Failed: {response.text}")
    
    # Check final cart
    print("\nFinal cart:")
    response = requests.get(f"{BASE_URL}/cart/?buyer_uid=12345")
    if response.status_code == 200:
        cart = response.json()
        print(f"   Total items: {len(cart['items'])}")
        print(f"   Total amount: ₱{cart['total_amount']}")

if __name__ == "__main__":
    test_cart_with_buyer_uid()
    test_more_items()
