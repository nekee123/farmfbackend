import requests
import json

base_url = "http://localhost:8000"

print("🧪 Testing Product Creation Endpoints")
print("=" * 50)

product_data = {
    "name": "Test Product",
    "type": "Fruits",
    "price": 50,
    "quantity": 10,
    "description": "Test product",
    "image": "test.jpg",
    "payment_methods": "CASH_ON_DELIVERY",
    "seller_uid": "36f3bae06452473585278253e37fe2da",
    "seller_name": "Niks Farme"
}

# Test wrong endpoint (what frontend is calling)
print("1. Testing WRONG endpoint: /products/")
try:
    response = requests.post(f"{base_url}/products/", json=product_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

print("\n2. Testing CORRECT endpoint: /api/products/")
try:
    response = requests.post(f"{base_url}/api/products/", json=product_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        print("   ✅ SUCCESS - Product created!")
        product = response.json()
        print(f"   Product UID: {product.get('uid')}")
        print(f"   Product Name: {product.get('name')}")
        print(f"   Price: ₱{product.get('price')}")
    else:
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 50)
print("🎯 SOLUTION:")
print("Frontend must call: POST /api/products/")
print("NOT: POST /products/")
