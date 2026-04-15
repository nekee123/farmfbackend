import requests
import json

base_url = "http://localhost:8000"

print("🔍 Checking ACTUAL Current Routes")
print("=" * 50)

# Test both with and without /api/ prefix
test_endpoints = [
    ("/sellers/", "Sellers without /api/"),
    ("/api/sellers/", "Sellers with /api/"),
    ("/products/", "Products without /api/"),
    ("/api/products/", "Products with /api/"),
    ("/buyers/", "Buyers without /api/"),
    ("/api/buyers/", "Buyers with /api/"),
]

print("Testing endpoints:")
for endpoint, description in test_endpoints:
    try:
        response = requests.get(f"{base_url}{endpoint}")
        print(f"✅ GET {endpoint:25} - {response.status_code} - {description}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"    └─ Returns {len(data)} items")
            else:
                print(f"    └─ Returns object")
        elif response.status_code == 404:
            print(f"    └─ Not Found")
        else:
            print(f"    └─ Status: {response.text[:30]}")
            
    except Exception as e:
        print(f"❌ GET {endpoint:25} - ERROR: {str(e)[:20]}")

print("\n" + "=" * 50)
print("🎯 What This Means:")
print("- If /api/ works: Routes have /api/ prefix")
print("- If /api/ doesn't work: Routes don't have /api/ prefix")
print("- Your frontend should match whatever actually works")
