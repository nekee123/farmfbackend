"""
Test script to verify login endpoints are working
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_buyer_signup_and_login():
    """Test buyer signup and login"""
    print("\n=== Testing Buyer Signup ===")
    signup_data = {
        "name": "Login Test Buyer",
        "phone_number": "+63987654323",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/buyers/", json=signup_data)
    print(f"Signup Status: {response.status_code}")
    if response.status_code == 201:
        buyer = response.json()
        print(f"Created Buyer: {buyer['name']} (UID: {buyer['uid']})")
        
        # Now test login
        print("\n=== Testing Buyer Login ===")
        login_data = {
            "phone_number": "+63987654323",
            "password": "testpass123"
        }
        login_response = requests.post(f"{BASE_URL}/buyers/login", json=login_data)
        print(f"Login Status: {login_response.status_code}")
        if login_response.status_code == 200:
            login_result = login_response.json()
            print("Login successful!")
            print(json.dumps(login_result, indent=2))
            return True
        else:
            print(f"Login Error: {login_response.text}")
            return False
    else:
        print(f"Signup Error: {response.text}")
        return False

def test_seller_signup_and_login():
    """Test seller signup and login"""
    print("\n=== Testing Seller Signup ===")
    signup_data = {
        "name": "Login Test Seller",
        "phone_number": "+63987654324",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/sellers/", json=signup_data)
    print(f"Signup Status: {response.status_code}")
    if response.status_code == 201:
        seller = response.json()
        print(f"Created Seller: {seller['name']} (UID: {seller['uid']})")
        
        # Now test login
        print("\n=== Testing Seller Login ===")
        login_data = {
            "phone_number": "+63987654324",
            "password": "testpass123"
        }
        login_response = requests.post(f"{BASE_URL}/sellers/login", json=login_data)
        print(f"Login Status: {login_response.status_code}")
        if login_response.status_code == 200:
            login_result = login_response.json()
            print("Login successful!")
            print(json.dumps(login_result, indent=2))
            return True
        else:
            print(f"Login Error: {login_response.text}")
            return False
    else:
        print(f"Signup Error: {response.text}")
        return False

def test_wrong_credentials():
    """Test login with wrong credentials"""
    print("\n=== Testing Wrong Credentials ===")
    login_data = {
        "phone_number": "+63987654323",
        "password": "wrongpassword"
    }
    response = requests.post(f"{BASE_URL}/buyers/login", json=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print(" Correctly rejected wrong password")
        return True
    else:
        print(f"❌ Unexpected response: {response.text}")
        return False

def main():
    print("=" * 50)
    print("Login Endpoint Tests")
    print("=" * 50)
    
    buyer_ok = test_buyer_signup_and_login()
    seller_ok = test_seller_signup_and_login()
    wrong_creds_ok = test_wrong_credentials()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Buyer Login: {'✅ PASS' if buyer_ok else '❌ FAIL'}")
    print(f"Seller Login: {'✅ PASS' if seller_ok else '❌ FAIL'}")
    print(f"Wrong Credentials: {'✅ PASS' if wrong_creds_ok else '❌ FAIL'}")
    print("=" * 50)

if __name__ == "__main__":
    main()
