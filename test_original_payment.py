import requests
import json

BASE_URL = "http://localhost:8000"

def test_original_payment_method():
    """Test the original payment method validation"""
    print("🧪 Testing Original Payment Method")
    print("=" * 40)
    
    # Test data with original frontend-friendly format
    order_data = {
        "buyer_uid": "938aad84601c4b88b1bbc7a836e3da01",
        "farm_product_uid": "afc36c142b86443ea2aec60822cd6b99",
        "quantity": 1,
        "payment_method": "Cash on Delivery"  # Original frontend format
    }
    
    print(f"\n1️⃣ Testing with: {order_data['payment_method']}")
    response = requests.post(f"{BASE_URL}/orders/", json=order_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        order = response.json()
        print(f"✅ Order created successfully!")
        print(f"   Order UID: {order['uid']}")
        print(f"   Payment Method: {order['payment_method']}")
        print(f"   Total Price: ₱{order['total_price']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_original_payment_method()
