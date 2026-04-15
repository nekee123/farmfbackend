import requests
import json

base_url = "http://localhost:8000"

# Test the updated schema with your frontend format
buyer_data = {
    "full_name": "Juan Dela Cruz",  # Changed from "name" to "full_name"
    "phone_number": "09808284536",
    "profile_picture": "base64_encoded_image_string",
    "password": "testpass123",
    "confirm_password": "testpass123"  # Added confirm password
}

print("Testing updated buyer schema with your frontend format:")
print(json.dumps(buyer_data, indent=2))

print("\n" + "=" * 50)
print("Test 1: Valid data with matching passwords")

try:
    response = requests.post(
        f"{base_url}/buyers/",
        json=buyer_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print("✅ SUCCESS - Buyer created with updated schema!")
        buyer_response = response.json()
        print(f"UID: {buyer_response.get('uid')}")
        print(f"Full Name: {buyer_response.get('full_name')}")
        print(f"Phone: {buyer_response.get('phone_number')}")
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
print("Test 2: Mismatched passwords")

buyer_data_mismatch = buyer_data.copy()
buyer_data_mismatch["confirm_password"] = "differentpass"

try:
    response = requests.post(
        f"{base_url}/buyers/",
        json=buyer_data_mismatch,
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
print("Updated Schema Summary:")
print("✅ full_name (instead of name)")
print("✅ phone_number (11 digits, starts with 09)")
print("✅ password")
print("✅ confirm_password (must match password)")
print("✅ profile_picture (optional)")
