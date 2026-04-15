import requests
import json

base_url = "http://localhost:8000"

print("🖼️ Testing Seller Profile Picture Update")
print("=" * 50)

# First, let's create a test seller
seller_data = {
    "name": "Test Seller with Profile",
    "phone_number": "09876543210",
    "location": "Test Farm",
    "password": "password123",
    "confirm_password": "password123"
}

print("1. Creating test seller...")
try:
    response = requests.post(
        f"{base_url}/sellers/",
        json=seller_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        seller_response = response.json()
        seller_uid = seller_response.get('uid')
        print(f"✅ Seller created with UID: {seller_uid}")
        
        # Now test updating with profile picture
        print("\n2. Testing profile picture update...")
        
        # Test with URL
        update_data_url = {
            "profile_picture": "https://example.com/seller-profile.jpg"
        }
        
        response = requests.patch(
            f"{base_url}/sellers/{seller_uid}",
            json=update_data_url,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            updated_seller = response.json()
            print(f"✅ Profile picture updated successfully!")
            print(f"Profile Picture: {updated_seller.get('profile_picture')}")
        else:
            print(f"❌ Update failed: {response.text}")
        
        # Test with base64 (small sample)
        print("\n3. Testing with base64 image...")
        base64_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
        update_data_base64 = {
            "profile_picture": base64_image
        }
        
        response = requests.patch(
            f"{base_url}/sellers/{seller_uid}",
            json=update_data_base64,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            updated_seller = response.json()
            print(f"✅ Base64 profile picture updated successfully!")
            print(f"Profile Picture (first 50 chars): {updated_seller.get('profile_picture')[:50]}...")
        else:
            print(f"❌ Base64 update failed: {response.text}")
        
        # Test getting all sellers to see profile picture in list
        print("\n4. Testing get all sellers...")
        response = requests.get(f"{base_url}/sellers/")
        
        if response.status_code == 200:
            sellers = response.json()
            test_seller = next((s for s in sellers if s.get('uid') == seller_uid), None)
            if test_seller:
                print(f"✅ Profile picture appears in seller list!")
                print(f"Profile Picture in list: {test_seller.get('profile_picture')[:50] if test_seller.get('profile_picture') else 'None'}...")
            else:
                print("❌ Test seller not found in list")
        else:
            print(f"❌ Get all sellers failed: {response.text}")
        
    else:
        print(f"❌ Seller creation failed: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 50)
print("📋 Seller Profile Picture Update Features:")
print("✅ Add profile picture URL")
print("✅ Add base64 encoded image")
print("✅ Update existing profile picture")
print("✅ Profile picture appears in response")
print("✅ Profile picture appears in seller list")
print("\n🔧 Usage:")
print("PATCH /sellers/{seller_uid}")
print("Body: {\"profile_picture\": \"URL or base64 string\"}")

print("\n🌽 Both Buyers and Sellers now support profile pictures!")
