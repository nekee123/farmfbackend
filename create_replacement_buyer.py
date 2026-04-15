import requests
import json

base_url = "http://localhost:8000"

# Create a replacement buyer with a different phone number
new_buyer = {
    "name": "Juan Dela Cruz",
    "phone_number": "09123456788",  # Changed last digit
    "password": "buyer123",
    "description": "Regular buyer from Manila (updated phone)"
}

print("Creating replacement for Juan Dela Cruz...")
print(f"Name: {new_buyer['name']}")
print(f"Phone: {new_buyer['phone_number']}")
print(f"Password: {new_buyer['password']}")

try:
    response = requests.post(
        f"{base_url}/buyers/",
        json={
            "name": new_buyer["name"],
            "phone_number": new_buyer["phone_number"],
            "password": new_buyer["password"]
        },
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print("✅ SUCCESS - New Juan Dela Cruz created!")
        buyer_data = response.json()
        print(f"UID: {buyer_data.get('uid')}")
    elif response.status_code == 400:
        print("⚠️  DUPLICATE - Phone number already exists")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ ERROR - {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 50)
print("Updated Buyer Credentials:")
print("1. Juan Dela Cruz (Updated)")
print("   Phone: 09123456788")
print("   Password: buyer123")
print("   Description: Regular buyer from Manila (updated phone)")
print("\n2. Maria Santos")
print("   Phone: 09987654321")
print("   Password: buyer456")
print("   Description: Buyer from Cebu")
print("\n3. Roberto Reyes")
print("   Phone: 09555555555")
print("   Password: buyer789")
print("   Description: Buyer from Davao")
print("\n4. Ana Garcia")
print("   Phone: 09750556999")
print("   Password: buyer000")
print("   Description: Buyer from Quezon City")
print("\n5. Carlos Mendoza")
print("   Phone: 09012345678")
print("   Password: buyer111")
print("   Description: Buyer from Laguna")
