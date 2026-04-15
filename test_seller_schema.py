import requests
import json

base_url = "http://localhost:8000"

# Test the updated seller schema without profile picture
seller_data = {
    "name": "Juan Dela Cruz Farms",
    "phone_number": "09808284534",
    "location": "Quezon City, Philippines",
    "password": "sellerpass123"
}

print("Testing updated seller schema (no profile picture):")
print(json.dumps(seller_data, indent=2))

print("\n" + "=" * 50)

try:
    response = requests.post(
        f"{base_url}/sellers/",
        json=seller_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print("✅ SUCCESS - Seller created without profile picture!")
        seller_response = response.json()
        print(f"UID: {seller_response.get('uid')}")
        print(f"Name: {seller_response.get('name')}")
        print(f"Phone: {seller_response.get('phone_number')}")
        print(f"Location: {seller_response.get('location', 'Not provided')}")
        print(f"Profile Picture: {seller_response.get('profile_picture', 'Not provided')}")
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
print("✅ Simplified Seller Schema Working!")
print("Fields required for seller account creation:")
print("- name")
print("- phone_number (11 digits, starts with 09)")
print("- location (optional)")
print("- password")
print("\nProfile picture is no longer required during registration!")
