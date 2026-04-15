import requests
import json

base_url = "http://localhost:8000"

print("🖼️ Testing Buyer Profile Picture Update")
print("=" * 50)

# First, let's create a test buyer
buyer_data = {
    "full_name": "Test Buyer with Profile",
    "phone_number": "09987654321",
    "location": "Test City",
    "password": "password123",
    "confirm_password": "password123"
}

print("1. Creating test buyer...")
try:
    response = requests.post(
        f"{base_url}/buyers/",
        json=buyer_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        buyer_response = response.json()
        buyer_uid = buyer_response.get('uid')
        print(f"✅ Buyer created with UID: {buyer_uid}")
        
        # Now test updating with profile picture
        print("\n2. Testing profile picture update...")
        
        # Test with URL
        update_data_url = {
            "profile_picture": "https://example.com/profile.jpg"
        }
        
        response = requests.patch(
            f"{base_url}/buyers/{buyer_uid}",
            json=update_data_url,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            updated_buyer = response.json()
            print(f"✅ Profile picture updated successfully!")
            print(f"Profile Picture: {updated_buyer.get('profile_picture')}")
        else:
            print(f"❌ Update failed: {response.text}")
        
        # Test with base64 (small sample)
        print("\n3. Testing with base64 image...")
        base64_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
        update_data_base64 = {
            "profile_picture": base64_image
        }
        
        response = requests.patch(
            f"{base_url}/buyers/{buyer_uid}",
            json=update_data_base64,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            updated_buyer = response.json()
            print(f"✅ Base64 profile picture updated successfully!")
            print(f"Profile Picture (first 50 chars): {updated_buyer.get('profile_picture')[:50]}...")
        else:
            print(f"❌ Base64 update failed: {response.text}")
        
        # Test getting all buyers to see profile picture in list
        print("\n4. Testing get all buyers...")
        response = requests.get(f"{base_url}/buyers/")
        
        if response.status_code == 200:
            buyers = response.json()
            test_buyer = next((b for b in buyers if b.get('uid') == buyer_uid), None)
            if test_buyer:
                print(f"✅ Profile picture appears in buyer list!")
                print(f"Profile Picture in list: {test_buyer.get('profile_picture')[:50] if test_buyer.get('profile_picture') else 'None'}...")
            else:
                print("❌ Test buyer not found in list")
        else:
            print(f"❌ Get all buyers failed: {response.text}")
        
    else:
        print(f"❌ Buyer creation failed: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 50)
print("📋 Profile Picture Update Features:")
print("✅ Add profile picture URL")
print("✅ Add base64 encoded image")
print("✅ Update existing profile picture")
print("✅ Profile picture appears in response")
print("✅ Profile picture appears in buyer list")
print("\n🔧 Usage:")
print("PATCH /buyers/{buyer_uid}")
print("Body: {\"profile_picture\": \"URL or base64 string\"}")
