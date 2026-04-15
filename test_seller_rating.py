import requests
import json

base_url = "http://localhost:8000"

print("⭐ Testing Seller Rating Endpoint")
print("=" * 50)

seller_uid = "ba4a5bd2c0104b7bbea27748b87b4d20"

print(f"1. Testing rating endpoint for seller: {seller_uid}")

# Test the rating endpoint
try:
    response = requests.get(f"{base_url}/api/sellers/{seller_uid}/rating")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        rating_data = response.json()
        print("✅ SUCCESS - Rating endpoint working!")
        print(f"Seller UID: {rating_data.get('seller_uid')}")
        print(f"Average Rating: {rating_data.get('average_rating')}")
        print(f"Review Count: {rating_data.get('review_count')}")
    elif response.status_code == 404:
        print("❌ 404 Not Found - Seller not found")
        error = response.json()
        print(f"Error: {error.get('detail', 'Unknown error')}")
    else:
        print(f"❌ ERROR - {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 50)
print("🔧 Available Seller Endpoints:")
print("✅ GET /api/sellers/{uid}/rating - Get seller rating")
print("✅ GET /api/sellers - Get all sellers")
print("✅ GET /api/sellers/{uid} - Get seller by UID")
print("✅ POST /api/sellers/login - Seller login")
print("✅ PATCH /api/sellers/{uid} - Update seller")
print("✅ DELETE /api/sellers/{uid} - Delete seller")

print("\n💡 Frontend Usage:")
print(f"GET {base_url}/api/sellers/{{seller_uid}}/rating")
