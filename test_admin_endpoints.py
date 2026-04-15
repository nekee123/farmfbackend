import requests
import json

base_url = "http://localhost:8000"

print("🔍 Testing Admin Endpoints")
print("=" * 50)

# Test 1: Check if admin login endpoint exists
print("1. Testing admin login endpoint...")
try:
    response = requests.post(
        f"{base_url}/admin/login",
        json={"username": "test", "password": "test"}
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 404:
        print("❌ Admin login endpoint not found")
    elif response.status_code == 401:
        print("✅ Admin login endpoint exists (wrong credentials expected)")
    else:
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)

# Test 2: Check main docs for admin routes
print("2. Checking main API docs...")
try:
    response = requests.get(f"{base_url}/docs")
    print(f"Main docs Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Main API docs accessible")
    else:
        print("❌ Main API docs not accessible")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)

# Test 3: Try to access admin docs (should fail without auth)
print("3. Testing admin docs (should require auth)...")
try:
    response = requests.get(f"{base_url}/admin/docs")
    print(f"Admin docs Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Admin docs properly protected (requires authentication)")
    elif response.status_code == 200:
        print("⚠️  Admin docs accessible without auth (security issue)")
    else:
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("🔧 Solutions:")
print("1. Use main docs: http://localhost:8000/docs")
print("2. Login first, then access admin endpoints")
print("3. Check if admin routes are properly registered")
