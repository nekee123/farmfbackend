import requests
import json

BASE_URL = "http://localhost:8000"

def test_payment_method_enum():
    """Test the new payment method enum validation"""
    print("🧪 Testing Payment Method Enum")
    print("=" * 40)
    
    # Test data
    order_data = {
        "buyer_uid": "938aad84601c4b88b1bbc7a836e3da01",  # Use existing buyer
        "farm_product_uid": "afc36c142b86443ea2aec60822cd6b99",  # Use existing product (Durian)
        "quantity": 1,
        "payment_method": "CASH_ON_DELIVERY"  # Use enum value
    }
    
    print(f"\n1️⃣ Testing with enum value: {order_data['payment_method']}")
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
        return
    
    # Test with MEET_UP_CASH_ON_PICKUP
    order_data["payment_method"] = "MEET_UP_CASH_ON_PICKUP"
    print(f"\n2️⃣ Testing with enum value: {order_data['payment_method']}")
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
    
    # Test with invalid payment method (should fail)
    order_data["payment_method"] = "INVALID_METHOD"
    print(f"\n3️⃣ Testing with invalid value: {order_data['payment_method']}")
    response = requests.post(f"{BASE_URL}/orders/", json=order_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 422:
        print(f"✅ Correctly rejected invalid payment method")
        print(f"   Error: {response.json()}")
    else:
        print(f"❌ Should have failed with 422, got: {response.text}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_payment_method_enum()
