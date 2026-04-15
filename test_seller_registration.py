import requests
import json

base_url = "http://localhost:8000"

print("🧪 Testing Seller Registration Endpoints")
print("=" * 50)

seller_data = {
    "name": "Test Seller",
    "phone_number": "09123456789",
    "password": "test123",
    "confirm_password": "test123",
    "location": "Test Location"
}

# Test wrong endpoint (what frontend is calling)
print("1. Testing WRONG endpoint: /sellers/")
try:
    response = requests.post(f"{base_url}/sellers/", json=seller_data)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

print("\n2. Testing CORRECT endpoint: /api/sellers/")
try:
    response = requests.post(f"{base_url}/api/sellers/", json=seller_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        print("   ✅ SUCCESS - Seller created!")
        seller = response.json()
        print(f"   Seller UID: {seller.get('uid')}")
        print(f"   Seller Name: {seller.get('name')}")
    else:
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 50)
print("🎯 SOLUTION:")
print("Frontend must call: POST /api/sellers/")
print("NOT: POST /sellers/")
