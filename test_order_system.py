"""
Test script to verify new order functionality
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_order_creation():
    """Test order creation with payment method"""
    print("\n=== Testing Order Creation ===")
    
    # First create a buyer and seller
    buyer_data = {
        "name": "Test Buyer",
        "phone_number": "+63987654325",
        "password": "testpass123"
    }
    
    seller_data = {
        "name": "Test Seller",
        "phone_number": "+63987654326",
        "password": "testpass123"
    }
    
    # Create buyer
    buyer_response = requests.post(f"{BASE_URL}/buyers/", json=buyer_data)
    if buyer_response.status_code != 201:
        print(f"❌ Failed to create buyer: {buyer_response.text}")
        return None
    
    buyer_uid = buyer_response.json()['uid']
    print(f"✅ Created buyer: {buyer_uid}")
    
    # Create seller
    seller_response = requests.post(f"{BASE_URL}/sellers/", json=seller_data)
    if seller_response.status_code != 201:
        print(f"❌ Failed to create seller: {seller_response.text}")
        return None
    
    seller_uid = seller_response.json()['uid']
    print(f"✅ Created seller: {seller_uid}")
    
    # Create a farm product
    product_data = {
        "name": "Test Farm Product",
        "type": "Vegetables",
        "price": 150.0,
        "quantity": 10,
        "description": "Fresh organic vegetables"
    }
    
    product_response = requests.post(f"{BASE_URL}/products/", json=product_data)
    if product_response.status_code != 201:
        print(f"❌ Failed to create product: {product_response.text}")
        return None
    
    product_uid = product_response.json()['uid']
    print(f"✅ Created product: {product_uid}")
    
    # Test order creation with valid payment method
    order_data = {
        "buyer_uid": buyer_uid,
        "farm_product_uid": product_uid,
        "quantity": 2,
        "payment_method": "Cash on Delivery"
    }
    
    order_response = requests.post(f"{BASE_URL}/orders/", json=order_data)
    print(f"Order creation status: {order_response.status_code}")
    if order_response.status_code == 201:
        order = order_response.json()
        print(f"✅ Order created successfully!")
        print(f"   Order UID: {order['uid']}")
        print(f"   Payment Method: {order['payment_method']}")
        print(f"   Order Status: {order['order_status']}")
        return order['uid']
    else:
        print(f"❌ Failed to create order: {order_response.text}")
        return None

def test_invalid_payment_method():
    """Test order creation with invalid payment method"""
    print("\n=== Testing Invalid Payment Method ===")
    
    order_data = {
        "buyer_uid": "test-buyer-uid",
        "farm_product_uid": "test-product-uid", 
        "quantity": 1,
        "payment_method": "Credit Card"  # Invalid payment method
    }
    
    response = requests.post(f"{BASE_URL}/orders/", json=order_data)
    print(f"Invalid payment method status: {response.status_code}")
    if response.status_code == 400:
        print("✅ Correctly rejected invalid payment method")
        print(f"   Error: {response.json()['detail']}")
        return True
    else:
        print("❌ Should have rejected invalid payment method")
        return False

def test_order_status_update():
    """Test order status update"""
    print("\n=== Testing Order Status Update ===")
    
    # First create an order to update
    order_uid = test_order_creation()
    if not order_uid:
        print("❌ Cannot test status update without valid order")
        return False
    
    # Test updating to Delivered
    status_data = {
        "order_status": "Delivered"
    }
    
    update_response = requests.patch(f"{BASE_URL}/orders/{order_uid}/status", json=status_data)
    print(f"Status update response: {update_response.status_code}")
    if update_response.status_code == 200:
        result = update_response.json()
        print("✅ Order status updated successfully!")
        print(f"   Message: {result['message']}")
        print(f"   New Status: {result['order_status']}")
        return True
    else:
        print(f"❌ Failed to update status: {update_response.text}")
        return False

def test_invalid_status_update():
    """Test invalid status update"""
    print("\n=== Testing Invalid Status Update ===")
    
    order_uid = test_order_creation()
    if not order_uid:
        print("❌ Cannot test invalid status without valid order")
        return False
    
    # Test updating to invalid status
    status_data = {
        "order_status": "Processing"  # Invalid - only "Delivered" allowed
    }
    
    response = requests.patch(f"{BASE_URL}/orders/{order_uid}/status", json=status_data)
    print(f"Invalid status update response: {response.status_code}")
    if response.status_code == 400:
        print("✅ Correctly rejected invalid status")
        print(f"   Error: {response.json()['detail']}")
        return True
    else:
        print("❌ Should have rejected invalid status")
        return False

def main():
    print("=" * 60)
    print("Order System Tests")
    print("=" * 60)
    
    # Run tests
    test_invalid_payment_method()
    test_order_status_update()
    test_invalid_status_update()
    
    print("\n" + "=" * 60)
    print("Order System Tests Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
