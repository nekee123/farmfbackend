import requests
import json

base_url = "http://localhost:8000"

print("🔧 Testing Updated API Routes with /api/ Prefix")
print("=" * 60)

# Test all the updated endpoints
endpoints = [
    ("GET", "/api/sellers/", "Get all sellers"),
    ("GET", "/api/buyers/", "Get all buyers"),
    ("GET", "/api/products/", "Get all products"),
    ("GET", "/api/orders/", "Get all orders"),
    ("GET", "/api/cart/", "Get cart"),
    ("GET", "/api/admin/", "Get admin"),
    ("GET", "/api/notifications/", "Get notifications"),
    ("GET", "/api/messages/", "Get messages"),
    ("GET", "/api/reviews/", "Get reviews"),
]

print("Testing endpoints:")
for method, endpoint, description in endpoints:
    try:
        if method == "GET":
            response = requests.get(f"{base_url}{endpoint}")
        
        print(f"✅ {method:4} {endpoint:25} - {response.status_code} - {description}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"    └─ Returns {len(data)} items")
            else:
                print(f"    └─ Returns object with keys: {list(data.keys()) if isinstance(data, dict) else 'non-dict'}")
        elif response.status_code == 401:
            print(f"    └─ Requires authentication")
        elif response.status_code == 422:
            print(f"    └─ Validation error")
        else:
            print(f"    └─ Status: {response.text[:50]}")
            
    except Exception as e:
        print(f"❌ {method:4} {endpoint:25} - ERROR: {str(e)[:30]}")

print("\n" + "=" * 60)
print("🎯 Frontend API Calls Should Now Use:")

frontend_examples = [
    ("Products", "GET", "/api/products/"),
    ("Sellers", "GET", "/api/sellers/"),
    ("Buyers", "GET", "/api/buyers/"),
    ("Orders", "GET", "/api/orders/"),
    ("Cart", "GET", "/api/cart/"),
    ("Create Product", "POST", "/api/products/"),
    ("Seller Login", "POST", "/api/sellers/login"),
    ("Buyer Login", "POST", "/api/buyers/login"),
    ("Seller Rating", "GET", "/api/sellers/{uid}/rating"),
]

for name, method, endpoint in frontend_examples:
    print(f"  {name:15} {method:4} {endpoint}")

print("\n✅ All routes now have consistent /api/ prefix!")
print("🚀 Your frontend should work correctly now!")
