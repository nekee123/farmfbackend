import requests
import json

base_url = "http://localhost:8000"

# Test with the exact schema format from your example
buyer_data = {
    "name": "Test User",
    "phone_number": "09808284536",  # Your example phone number
    "profile_picture": "base64_encoded_image_string",
    "password": "testpass123"
}

print("Testing buyer creation with your schema format:")
print(json.dumps(buyer_data, indent=2))

try:
    response = requests.post(
        f"{base_url}/buyers/",
        json=buyer_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print("✅ SUCCESS - Buyer created with your schema format!")
        buyer_response = response.json()
        print(f"UID: {buyer_response.get('uid')}")
        print(f"Name: {buyer_response.get('name')}")
        print(f"Phone: {buyer_response.get('phone_number')}")
    elif response.status_code == 400:
        print("⚠️  VALIDATION ERROR - Check the format")
        error = response.json()
        print(f"Error: {error.get('detail', 'Unknown error')}")
    else:
        print(f"❌ ERROR - {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")
