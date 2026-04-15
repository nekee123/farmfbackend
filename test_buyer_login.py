import requests
import json

base_url = "http://localhost:8000"

# Test buyer login with existing user
login_data = {
    "phone_number": "09808284535",  # Maria Santos from earlier test
    "password": "testpass123"
}

print("Testing Buyer Login")
print("=" * 50)
print("Login Credentials:")
print(f"Phone: {login_data['phone_number']}")
print(f"Password: {login_data['password']}")
print()

try:
    response = requests.post(
        f"{base_url}/buyers/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS - Buyer login successful!")
        login_result = response.json()
        print(f"UID: {login_result.get('uid')}")
        print(f"Name: {login_result.get('name')}")
        print(f"Phone: {login_result.get('phone_number')}")
        print(f"Access Token: {login_result.get('access_token', 'N/A')}")
    else:
        print(f"❌ ERROR - {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 50)
print("SAMPLE BUYER USER FOR TESTING")
print("=" * 50)
print("👤 Name: Maria Santos")
print("📱 Phone: 09808284535")
print("🔑 Password: testpass123")
print()
print("This user was created during previous tests and should work for:")
print("• Buyer login in frontend")
print("• Making purchases")
print("• Viewing orders")
print("• Managing profile")
