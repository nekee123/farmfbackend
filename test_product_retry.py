import requests
import json
import time

base_url = "http://localhost:8000"

print("🌾 Testing Product Creation with Retry Logic")
print("=" * 60)

# Test product data
product_data = {
    "name": "Test Product with Retry",
    "type": "Fruits",
    "price": 50,
    "quantity": 3,
    "description": "Testing improved error handling",
    "image": "string",
    "payment_methods": "CASH_ON_DELIVERY,MEET_UP_CASH_ON_PICKUP",
    "seller_uid": "ba4a5bd2c0104b7bbea27748b87b4d20",
    "seller_name": "Test Seller"
}

print("1. Creating product with improved error handling...")
print(f"Product data: {json.dumps(product_data, indent=2)}")

start_time = time.time()

try:
    response = requests.post(
        f"{base_url}/products/",
        json=product_data,
        headers={"Content-Type": "application/json"},
        timeout=30  # 30 second timeout
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Time: {duration:.2f} seconds")
    
    if response.status_code == 201:
        print("✅ SUCCESS - Product created!")
        product_response = response.json()
        print(f"Product UID: {product_response.get('uid')}")
        print(f"Product Name: {product_response.get('name')}")
        print(f"Price: ₱{product_response.get('price')}")
        print(f"Seller: {product_response.get('seller_name')}")
        print(f"Location: {product_response.get('seller_location')}")
    elif response.status_code == 503:
        print("⚠️  Database unavailable - retry logic triggered")
        error = response.json()
        print(f"Error: {error.get('detail', 'Unknown error')}")
    else:
        print(f"❌ ERROR - {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("❌ TIMEOUT - Request took too long")
except requests.exceptions.ConnectionError:
    print("❌ CONNECTION ERROR - Server not reachable")
except Exception as e:
    print(f"❌ EXCEPTION: {e}")

print("\n" + "=" * 60)
print("🔧 Improvements Made:")
print("✅ Added retry logic for Neo4j connection issues")
print("✅ Better error handling for ServiceUnavailable")
print("✅ Better error handling for SessionExpired")
print("✅ Increased timeout to 30 seconds")
print("✅ More informative error messages")

print("\n💡 Frontend Tips:")
print("1. Set request timeout to 30+ seconds")
print("2. Handle 503 errors gracefully")
print("3. Show loading states during product creation")
print("4. Retry failed requests automatically")
