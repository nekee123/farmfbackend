import requests
import json

base_url = "http://localhost:8000"

print("Testing Buyer Login:")
print("=" * 50)

# Test buyer login with created user
buyer_login_data = {
    "phone_number": "09808284532",
    "password": "buyerpass123"
}

print(f"Login data: {json.dumps(buyer_login_data, indent=2)}")

try:
    response = requests.post(
        f"{base_url}/buyers/login",
        json=buyer_login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS - Buyer login successful!")
        login_response = response.json()
        print(f"Response: {json.dumps(login_response, indent=2)}")
    elif response.status_code == 401:
        print("❌ ERROR - Invalid credentials")
        print(f"Response: {response.json()}")
    elif response.status_code == 404:
        print("❌ ERROR - User not found")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ ERROR - {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 50)
print("Testing Seller Login:")

# Test seller login with created user
seller_login_data = {
    "phone_number": "09808284533",
    "password": "sellerpass123"
}

print(f"Login data: {json.dumps(seller_login_data, indent=2)}")

try:
    response = requests.post(
        f"{base_url}/sellers/login",
        json=seller_login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS - Seller login successful!")
        login_response = response.json()
        print(f"Response: {json.dumps(login_response, indent=2)}")
    elif response.status_code == 401:
        print("❌ ERROR - Invalid credentials")
        print(f"Response: {response.json()}")
    elif response.status_code == 404:
        print("❌ ERROR - User not found")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ ERROR - {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 50)
print("Debugging Tips:")
print("1. Make sure server is running: http://localhost:8000/docs")
print("2. Check phone number format: 11 digits starting with 09")
print("3. Verify password is correct")
print("4. Check if user exists in database")
print("5. Check CORS settings if calling from frontend")
