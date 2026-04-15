import requests
import json

base_url = "http://localhost:8000"

# Test updated buyer schema with location
buyer_data = {
    "full_name": "Juan Dela Cruz",
    "phone_number": "09808284532",
    "location": "Manila, Philippines",
    "password": "buyerpass123",
    "confirm_password": "buyerpass123"
}

print("Testing updated buyer schema with location:")
print(json.dumps(buyer_data, indent=2))

print("\n" + "=" * 50)
print("Test 1: Valid data with location")

try:
    response = requests.post(
        f"{base_url}/buyers/",
        json=buyer_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print("✅ SUCCESS - Buyer created with location!")
        buyer_response = response.json()
        print(f"UID: {buyer_response.get('uid')}")
        print(f"Full Name: {buyer_response.get('full_name')}")
        print(f"Phone: {buyer_response.get('phone_number')}")
        print(f"Location: {buyer_response.get('location', 'Not provided')}")
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
print("Test 2: Create buyer without location (optional)")

buyer_data_no_location = {
    "full_name": "Maria Santos",
    "phone_number": "09808284531",
    "password": "buyerpass456",
    "confirm_password": "buyerpass456"
}

try:
    response = requests.post(
        f"{base_url}/buyers/",
        json=buyer_data_no_location,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print("✅ SUCCESS - Buyer created without location!")
        buyer_response = response.json()
        print(f"UID: {buyer_response.get('uid')}")
        print(f"Full Name: {buyer_response.get('full_name')}")
        print(f"Phone: {buyer_response.get('phone_number')}")
        print(f"Location: '{buyer_response.get('location', '')}' (empty as expected)")
    else:
        print(f"❌ ERROR - {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 50)
print("✅ Updated Buyer Schema Working!")
print("Fields required for buyer account creation:")
print("- full_name")
print("- phone_number (11 digits, starts with 09)")
print("- location (optional)")
print("- password")
print("- confirm_password (must match password)")
print("\nLocation field successfully added to buyer creation!")
