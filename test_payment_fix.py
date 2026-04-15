import requests

def test_payment_fix():
    """Test the payment method fix"""
    print("🧪 Testing Payment Method Fix")
    print("=" * 40)
    
    order_data = {
        "buyer_uid": "938aad84601c4b88b1bbc7a836e3da01",
        "farm_product_uid": "a3c871f40c2a4ff9afec5100114a1cbb",  # Durian product
        "quantity": 1,
        "payment_method": "Meet Up / Cash on Pick-up"  # Exact database format
    }
    
    print(f"Testing with: '{order_data['payment_method']}'")
    response = requests.post("http://localhost:8000/orders/", json=order_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        order = response.json()
        print(f"✅ Success! Order created")
        print(f"   Order UID: {order['uid']}")
        print(f"   Payment Method: {order['payment_method']}")
    else:
        print(f"❌ Failed: {response.text}")

if __name__ == "__main__":
    test_payment_fix()
