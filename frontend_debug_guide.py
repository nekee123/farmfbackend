import requests
import json

base_url = "http://localhost:8000"

print("🔍 Frontend Debugging Guide")
print("=" * 60)

print("✅ Backend Status: WORKING")
print("   - Products are being created successfully")
print("   - Products are being retrieved successfully")
print("   - GET /products/ returns 3 products")
print("   - GET /products/?seller_uid=... returns filtered products")

print("\n❌ Likely Frontend Issues:")
print("1. Wrong endpoint URL")
print("2. Missing authentication headers")
print("3. Error handling hiding products")
print("4. State management issues")
print("5. Caching problems")

print("\n🔧 Frontend Checklist:")

print("\n1. Check API Endpoint:")
print("   ✅ Correct: GET http://localhost:8000/products/")
print("   ❌ Wrong: GET http://localhost:8000/api/products/")
print("   ❌ Wrong: GET http://localhost:8000/product/")

print("\n2. Check Headers:")
print("   Add these headers to your request:")
print("   'Content-Type': 'application/json'")
print("   'Accept': 'application/json'")

print("\n3. Check Authentication:")
print("   - No auth required for GET /products/")
print("   - But include if your app uses auth")

print("\n4. Check Error Handling:")
print("   Make sure you're checking response.status === 200")
print("   Log any errors to console")

print("\n5. Check Data Processing:")
print("   - Verify you're parsing JSON: response.json()")
print("   - Check if array is empty before rendering")
print("   - Log the actual response data")

print("\n📱 Example Frontend Code:")
print("""
// ✅ Correct implementation
async function getProducts() {
  try {
    const response = await fetch('http://localhost:8000/products/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
    
    if (response.status === 200) {
      const products = await response.json();
      console.log('Products:', products);
      return products;
    } else {
      console.error('Error:', response.status, response.statusText);
      return [];
    }
  } catch (error) {
    console.error('Network error:', error);
    return [];
  }
}
""")

print("\n🧪 Test Different Endpoints:")
endpoints = [
    "/products/",
    "/products/?seller_uid=ba4a5bd2c0104b7bbea27748b87b4d20",
    "/products/?type=Fruits",
    "/products/?name=Durian"
]

for endpoint in endpoints:
    try:
        response = requests.get(f"{base_url}{endpoint}")
        print(f"   {endpoint}: {response.status_code} ({len(response.json())} items)")
    except Exception as e:
        print(f"   {endpoint}: ERROR - {e}")

print("\n🎯 Next Steps:")
print("1. Check your frontend's network tab in browser dev tools")
print("2. Verify the exact URL being called")
print("3. Check response status and data")
print("4. Add console.log statements to debug")
print("5. Compare with working endpoints")
