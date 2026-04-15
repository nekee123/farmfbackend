import requests
import json

base_url = "http://localhost:8000"

print("🌾 Testing Product Retrieval")
print("=" * 50)

print("1. Testing get all products...")
try:
    response = requests.get(f"{base_url}/products/")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        products = response.json()
        print(f"✅ Found {len(products)} products")
        
        if products:
            for i, product in enumerate(products[:3]):  # Show first 3
                print(f"\nProduct {i+1}:")
                print(f"  UID: {product.get('uid')}")
                print(f"  Name: {product.get('name')}")
                print(f"  Type: {product.get('type')}")
                print(f"  Price: ₱{product.get('price')}")
                print(f"  Seller: {product.get('seller_name')}")
                print(f"  Seller UID: {product.get('seller_uid')}")
        else:
            print("❌ No products found!")
            
    else:
        print(f"❌ ERROR - {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 50)
print("2. Testing products by specific seller...")

seller_uid = "ba4a5bd2c0104b7bbea27748b87b4d20"
try:
    response = requests.get(f"{base_url}/products/?seller_uid={seller_uid}")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        products = response.json()
        print(f"✅ Found {len(products)} products for seller {seller_uid}")
        
        if products:
            for i, product in enumerate(products):
                print(f"\nProduct {i+1}:")
                print(f"  Name: {product.get('name')}")
                print(f"  Price: ₱{product.get('price')}")
        else:
            print("❌ No products found for this seller!")
            
    else:
        print(f"❌ ERROR - {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 50)
print("3. Creating a test product to verify...")
test_product = {
    "name": "Debug Test Product",
    "type": "Vegetables",
    "price": 25,
    "quantity": 5,
    "description": "Testing product display",
    "image": "test.jpg",
    "payment_methods": "CASH_ON_DELIVERY,MEET_UP_CASH_ON_PICKUP",
    "seller_uid": seller_uid,
    "seller_name": "Debug Seller"
}

try:
    response = requests.post(f"{base_url}/products/", json=test_product)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        created_product = response.json()
        print("✅ Test product created!")
        print(f"  UID: {created_product.get('uid')}")
        print(f"  Name: {created_product.get('name')}")
        
        # Now check if it appears in the list
        print("\n4. Checking if new product appears in list...")
        list_response = requests.get(f"{base_url}/products/")
        if list_response.status_code == 200:
            updated_products = list_response.json()
            print(f"✅ Now showing {len(updated_products)} products")
            
            # Find our test product
            test_product_in_list = next((p for p in updated_products if p.get('uid') == created_product.get('uid')), None)
            if test_product_in_list:
                print("✅ Test product found in list!")
                print(f"  Name: {test_product_in_list.get('name')}")
                print(f"  Seller: {test_product_in_list.get('seller_name')}")
            else:
                print("❌ Test product NOT found in list!")
    else:
        print(f"❌ Failed to create test product: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 50)
print("🔍 Diagnosis:")
print("If products are created but not showing, the issue is likely:")
print("1. Missing SOLD_BY relationship between product and seller")
print("2. Query not finding products without seller relationships")
print("3. Frontend calling wrong endpoint")
