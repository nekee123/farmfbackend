import requests
import json

BASE_URL = "http://localhost:8000"

def test_cart_endpoints():
    """Test all cart endpoints"""
    
    # First login as buyer to get token
    print("=== Login as Buyer ===")
    login_data = {
        "phone_number": "+639123456789",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/buyer/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test 1: Get cart (should be empty initially)
    print("\n=== Test 1: Get Cart ===")
    try:
        response = requests.get(f"{BASE_URL}/cart/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            cart = response.json()
            print(f"Cart items: {len(cart['items'])}")
            print(f"Total amount: {cart['total_amount']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Add item to cart
    print("\n=== Test 2: Add Item to Cart ===")
    item_data = {
        "product_uid": "test-product-123",
        "quantity": 2,
        "price_at_time": 150.50
    }
    
    try:
        response = requests.post(f"{BASE_URL}/cart/items", json=item_data, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            item = response.json()
            print(f"Item added: {item['uid']}, Quantity: {item['quantity']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Get cart summary
    print("\n=== Test 3: Get Cart Summary ===")
    try:
        response = requests.get(f"{BASE_URL}/cart/summary", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            summary = response.json()
            print(f"Total items: {summary['total_items']}")
            print(f"Total amount: {summary['total_amount']}")
            print(f"Items count: {summary['items_count']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Update cart item
    print("\n=== Test 4: Update Cart Item ===")
    update_data = {"quantity": 5}
    
    try:
        response = requests.put(f"{BASE_URL}/cart/items/test-item-123", json=update_data, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            item = response.json()
            print(f"Item updated: Quantity = {item['quantity']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Remove item from cart
    print("\n=== Test 5: Remove Item from Cart ===")
    try:
        response = requests.delete(f"{BASE_URL}/cart/items/test-item-123", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Item removed successfully")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 6: Clear cart
    print("\n=== Test 6: Clear Cart ===")
    try:
        response = requests.delete(f"{BASE_URL}/cart/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Cart cleared successfully")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_cart_endpoints()
