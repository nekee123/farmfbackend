import requests
import json

base_url = "http://localhost:8000"

# Test the failing user
buyer_data = {
    "name": "Juan Dela Cruz",
    "phone_number": "09123456789",
    "password": "buyer123"
}

print("Testing Juan Dela Cruz creation...")
print(f"Data: {json.dumps(buyer_data, indent=2)}")

try:
    response = requests.post(
        f"{base_url}/buyers/",
        json=buyer_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 500:
        print(f"Response Text: {response.text}")
    else:
        try:
            response_json = response.json()
            print(f"Response Body: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response Body: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")

# Also check if this user already exists
print("\nChecking if user already exists...")
try:
    response = requests.post(
        f"{base_url}/buyers/login",
        json={
            "phone_number": "09123456789",
            "password": "buyer123"
        },
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Login Status Code: {response.status_code}")
    if response.status_code == 200:
        print("User already exists and login works")
        print(f"Response: {response.json()}")
    else:
        print(f"Login failed: {response.text}")
        
except Exception as e:
    print(f"Login check exception: {e}")
