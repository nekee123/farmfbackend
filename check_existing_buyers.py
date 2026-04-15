import requests
import json

base_url = "http://localhost:8000"

print("Checking existing buyers...")
print("=" * 50)

try:
    response = requests.get(f"{base_url}/buyers/")
    
    if response.status_code == 200:
        buyers = response.json()
        print(f"Found {len(buyers)} buyers:")
        
        for i, buyer in enumerate(buyers, 1):
            print(f"\n{i}. {buyer['name']}")
            print(f"   Phone: {buyer['phone_number']}")
            print(f"   UID: {buyer['uid']}")
            
            # Check if this is the problematic phone number
            if buyer['phone_number'] == '09123456789':
                print("   ⚠️  This is the phone number that's causing issues!")
    else:
        print(f"Error fetching buyers: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 50)

# Now try to create the user again to see if the fix worked
print("\nTrying to create Juan Dela Cruz again...")

buyer_data = {
    "name": "Juan Dela Cruz",
    "phone_number": "09123456789",
    "password": "buyer123"
}

try:
    response = requests.post(
        f"{base_url}/buyers/",
        json=buyer_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200 or response.status_code == 201:
        print("✅ SUCCESS - Juan Dela Cruz created!")
        print(f"Response: {response.json()}")
    elif response.status_code == 400:
        print("⚠️  DUPLICATE - Phone number already exists")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ ERROR - {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")
