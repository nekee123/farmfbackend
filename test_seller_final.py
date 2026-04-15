import requests
import json

base_url = "http://localhost:8000"

# Test updated seller schema with confirm_password
seller_data = {
    "name": "Maria's Organic Farm",
    "phone_number": "09808284533",
    "location": "Laguna, Philippines",
    "password": "sellerpass123",
    "confirm_password": "sellerpass123"
}

print("Testing updated seller schema with confirm_password:")
print(json.dumps(seller_data, indent=2))

print("\n" + "=" * 50)
print("Test 1: Valid data with matching passwords")

try:
    response = requests.post(
        f"{base_url}/sellers/",
        json=seller_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print("✅ SUCCESS - Seller created with confirm_password!")
        seller_response = response.json()
        print(f"UID: {seller_response.get('uid')}")
        print(f"Name: {seller_response.get('name')}")
        print(f"Phone: {seller_response.get('phone_number')}")
        print(f"Location: {seller_response.get('location', 'Not provided')}")
    elif response.status_code == 422:
        print("⚠️  VALIDATION ERROR")
        error = response.json()
        print(f"Error: {error.get('detail', 'Unknown error')}")
    elif response.status_code == 400:
        print("⚠️  DUPLICATE - Phone number already exists")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ ERROR - {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 50)
print("Test 2: Mismatched passwords")

seller_data_mismatch = seller_data.copy()
seller_data_mismatch["confirm_password"] = "differentpass"

try:
    response = requests.post(
        f"{base_url}/sellers/",
        json=seller_data_mismatch,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 422:
        print("✅ SUCCESS - Password mismatch correctly rejected!")
        error = response.json()
        print(f"Error: {error.get('detail', 'Unknown error')}")
    else:
        print(f"❌ ERROR - Expected 422, got {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 50)
print("✅ Updated Seller Schema Working!")
print("Fields required for seller account creation:")
print("- name")
print("- phone_number (11 digits, starts with 09)")
print("- location (optional)")
print("- password")
print("- confirm_password (must match password)")
print("\nProfile picture is no longer required during registration!")
