import requests
import json

base_url = "http://localhost:8000"

print("🔍 Testing Product Display Issue")
print("=" * 50)

print("1. Testing all products retrieval...")
try:
    response = requests.get(f"{base_url}/api/products/")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        products = response.json()
        print(f"   ✅ Found {len(products)} products")
        
        # Look for the recently created product
        test_product_uid = "cde91595c50a4a228d4299f38203b105"
        found_product = next((p for p in products if p.get('uid') == test_product_uid), None)
        
        if found_product:
            print(f"   ✅ Found your product:")
            print(f"      Name: {found_product.get('name')}")
            print(f"      Price: ₱{found_product.get('price')}")
            print(f"      Seller: {found_product.get('seller_name')}")
        else:
            print(f"   ❌ Your product not found in list")
            print(f"   Looking for UID: {test_product_uid}")
            
        # Show all product UIDs for debugging
        print(f"   All product UIDs:")
        for i, product in enumerate(products):
            print(f"      {i+1}. {product.get('uid')} - {product.get('name')}")
            
    else:
        print(f"   ❌ Error: {response.text}")
        
except Exception as e:
    print(f"   Exception: {e}")

print("\n2. Testing products by specific seller...")
seller_uid = "36f3bae06452473585278253e37fe2da"
try:
    response = requests.get(f"{base_url}/api/products/?seller_uid={seller_uid}")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        seller_products = response.json()
        print(f"   ✅ Found {len(seller_products)} products for this seller")
        
        for i, product in enumerate(seller_products):
            print(f"      {i+1}. {product.get('name')} - ₱{product.get('price')}")
    else:
        print(f"   ❌ Error: {response.text}")
        
except Exception as e:
    print(f"   Exception: {e}")

print("\n3. Testing direct product lookup...")
test_product_uid = "cde91595c50a4a228d4299f38203b105"
try:
    response = requests.get(f"{base_url}/api/products/{test_product_uid}")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        product = response.json()
        print(f"   ✅ Found product directly:")
        print(f"      Name: {product.get('name')}")
        print(f"      Price: ₱{product.get('price')}")
        print(f"      Seller: {product.get('seller_name')}")
    else:
        print(f"   ❌ Error: {response.text}")
        
except Exception as e:
    print(f"   Exception: {e}")

print("\n" + "=" * 50)
print("🎯 Diagnosis:")
print("- If all products work but seller-specific doesn't, frontend is using wrong filter")
print("- If direct lookup works but list doesn't, there's a query issue")
print("- If nothing works, frontend is calling wrong endpoint")
