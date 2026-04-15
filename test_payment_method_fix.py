import requests
import json

base_url = "http://localhost:8000"

print("Testing Payment Method Fix")
print("=" * 50)

# Test order creation with frontend payment method format
order_data = {
    "farm_product_uid": "cde91595c50a4a228d4299f38203b105",  # Existing product
    "buyer_uid": "d0c6757a4f55402ca2db2de819f4138b",  # Existing buyer
    "quantity": 1,
    "payment_method": "Meet Up / Cash on Pick-up"  # Frontend format
}

print("1. Testing order with 'Meet Up / Cash on Pick-up' (frontend format)")
print(f"   Product UID: {order_data['farm_product_uid']}")
print(f"   Buyer UID: {order_data['buyer_uid']}")
print(f"   Payment Method: {order_data['payment_method']}")

try:
    response = requests.post(f"{base_url}/api/orders/", json=order_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 201:
        order = response.json()
        print("   Order created successfully!")
        print(f"   Order UID: {order.get('uid')}")
        print(f"   Payment Method: {order.get('payment_method')}")
        print(f"   Total: ${order.get('total_amount')}")
    else:
        print(f"   Error: {response.text}")
        
except Exception as e:
    print(f"   Exception: {e}")

print("\n2. Testing order with 'Cash on Delivery' (frontend format)")
order_data["payment_method"] = "Cash on Delivery"

try:
    response = requests.post(f"{base_url}/api/orders/", json=order_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 201:
        order = response.json()
        print("   Order created successfully!")
        print(f"   Order UID: {order.get('uid')}")
        print(f"   Payment Method: {order.get('payment_method')}")
    else:
        print(f"   Error: {response.text}")
        
except Exception as e:
    print(f"   Exception: {e}")

print("\n3. Testing invalid payment method")
order_data["payment_method"] = "Invalid Method"

try:
    response = requests.post(f"{base_url}/api/orders/", json=order_data)
    print(f"   Status: {response.status_code}")
    print(f"   Expected error: {response.text}")
    
except Exception as e:
    print(f"   Exception: {e}")

print("\n" + "=" * 50)
print("Expected Results:")
print("1. 'Meet Up / Cash on Pick-up' should work (201)")
print("2. 'Cash on Delivery' should work (201)")
print("3. 'Invalid Method' should fail (400)")
