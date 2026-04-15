"""
Test script to verify all endpoints are working correctly
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_create_buyer():
    """Test buyer creation"""
    print("\n=== Testing Buyer Creation ===")
    data = {
        "name": "Test Buyer",
        "phone_number": "+63987654327",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/buyers/", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        buyer = response.json()
        print(f"Created Buyer UID: {buyer['uid']}")
        return buyer['uid']
    else:
        print(f"Error: {response.text}")
        return None

def test_update_buyer(buyer_uid):
    """Test buyer profile update"""
    print("\n=== Testing Buyer Profile Update ===")
    data = {
        "name": "Updated Buyer Name"
    }
    response = requests.patch(f"{BASE_URL}/buyers/{buyer_uid}", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Buyer updated successfully")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")

def test_create_seller():
    """Test seller creation"""
    print("\n=== Testing Seller Creation ===")
    data = {
        "name": "Test Seller",
        "phone_number": "+63987654328",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/sellers/", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        seller = response.json()
        print(f"Created Seller UID: {seller['uid']}")
        return seller['uid'], seller['name']
    else:
        print(f"Error: {response.text}")
        return None, None

def test_update_seller(seller_uid):
    """Test seller profile update"""
    print("\n=== Testing Seller Profile Update ===")
    data = {
        "name": "Updated Seller Name"
    }
    response = requests.patch(f"{BASE_URL}/sellers/{seller_uid}", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Seller updated successfully")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")

def test_create_product(seller_uid, seller_name):
    """Test product creation"""
    print("\n=== Testing Product Creation ===")
    data = {
        "name": "Fresh Tilapia",
        "type": "Freshwater",
        "price": 150.0,
        "quantity": 50,
        "description": "Fresh from the farm",
        "seller_uid": seller_uid,
        "seller_name": seller_name
    }
    response = requests.post(f"{BASE_URL}/products/", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        product = response.json()
        print(f"Created Product UID: {product['uid']}")
        return product['uid'], product['name'], product['price']
    else:
        print(f"Error: {response.text}")
        return None, None, None

def test_create_order(buyer_uid, seller_uid, product_uid, product_name, price):
    """Test order creation (Buy Now)"""
    print("\n=== Testing Order Creation (Buy Now) ===")
    data = {
        "buyer_uid": buyer_uid,
        "buyer_name": "Test Buyer",
        "seller_uid": seller_uid,
        "seller_name": "Test Seller",
        "farm_product_uid": product_uid,
        "farm_product_name": product_name,
        "quantity": 1,
        "total_price": price
    }
    response = requests.post(f"{BASE_URL}/orders/", json=data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        order = response.json()
        print("Order created successfully!")
        print(json.dumps(order, indent=2))
        return order['uid']
    else:
        print(f"Error: {response.text}")
        return None

def main():
    print("=" * 50)
    print("FarmFresh Connect API Endpoint Tests")
    print("=" * 50)
    
    # Test buyer endpoints
    buyer_uid = test_create_buyer()
    if buyer_uid:
        test_update_buyer(buyer_uid)
    
    # Test seller endpoints
    seller_uid, seller_name = test_create_seller()
    if seller_uid:
        test_update_seller(seller_uid)
    
    # Test product endpoints
    if seller_uid:
        product_uid, product_name, price = test_create_product(seller_uid, seller_name)
        
        # Test order endpoints (Buy Now)
        if product_uid and buyer_uid:
            test_create_order(buyer_uid, seller_uid, product_uid, product_name, price)
    
    print("\n" + "=" * 50)
    print("Tests completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()
