import requests
import json

base_url = "http://localhost:8000"

# Test the simplified schema without profile picture
buyer_data = {
    "full_name": "Juan Dela Cruz",
    "phone_number": "09808284536",
    "password": "testpass123",
    "confirm_password": "testpass123"
}

print("Testing simplified buyer schema (no profile picture):")
print(json.dumps(buyer_data, indent=2))

print("\n" + "=" * 50)

try:
    response = requests.post(
        f"{base_url}/buyers/",
        json=buyer_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print("✅ SUCCESS - Buyer created without profile picture!")
        buyer_response = response.json()
        print(f"UID: {buyer_response.get('uid')}")
        print(f"Full Name: {buyer_response.get('full_name')}")
        print(f"Phone: {buyer_response.get('phone_number')}")
        print(f"Profile Picture: {buyer_response.get('profile_picture', 'Not provided')}")
    elif response.status_code == 422:
        print("⚠️  VALIDATION ERROR")
        error = response.json()
        print(f"Error: {error.get('detail', 'Unknown error')}")
    else:
        print(f"❌ ERROR - {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 50)
print("Simplified Schema Summary:")
print("✅ full_name")
print("✅ phone_number (11 digits, starts with 09)")
print("✅ password")
print("✅ confirm_password (must match password)")
print("❌ profile_picture (removed from creation)")
print("\nNote: Profile picture can be added later via a separate update endpoint")
