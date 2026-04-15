# Test Users for IsdaMarket Backend
# All phone numbers follow the new validation: 11 digits starting with 09

import requests
import json

base_url = "http://localhost:8000"

# Test Buyers
buyers = [
    {
        "name": "Juan Dela Cruz",
        "phone_number": "09123456789",
        "password": "buyer123",
        "description": "Regular buyer from Manila"
    },
    {
        "name": "Maria Santos",
        "phone_number": "09987654321", 
        "password": "buyer456",
        "description": "Buyer from Cebu"
    },
    {
        "name": "Roberto Reyes",
        "phone_number": "09555555555",
        "password": "buyer789",
        "description": "Buyer from Davao"
    },
    {
        "name": "Ana Garcia",
        "phone_number": "09750556999",
        "password": "buyer000",
        "description": "Buyer from Quezon City"
    },
    {
        "name": "Carlos Mendoza",
        "phone_number": "09012345678",
        "password": "buyer111",
        "description": "Buyer from Laguna"
    }
]

# Test Sellers
sellers = [
    {
        "name": "Farms of Laguna",
        "phone_number": "09111111111",
        "password": "seller123",
        "location": "Laguna, Philippines",
        "description": "Vegetable farm specializing in organic produce"
    },
    {
        "name": "Cebu Fresh Fruits",
        "phone_number": "09222222222",
        "password": "seller456", 
        "location": "Cebu City, Philippines",
        "description": "Tropical fruits supplier"
    },
    {
        "name": "Davao Dairy Farm",
        "phone_number": "09333333333",
        "password": "seller789",
        "location": "Davao del Sur, Philippines", 
        "description": "Fresh dairy products and milk"
    },
    {
        "name": "Benguet Highlands",
        "phone_number": "09444444444",
        "password": "seller000",
        "location": "Benguet, Philippines",
        "description": "Highland vegetables and strawberries"
    },
    {
        "name": "Ilocos Rice Fields",
        "phone_number": "09555555555",
        "password": "seller111",
        "location": "Ilocos Norte, Philippines",
        "description": "Premium rice varieties"
    }
]

def create_test_users():
    """Create test users in the system"""
    
    print("Creating Test Buyers")
    print("=" * 50)
    
    for i, buyer in enumerate(buyers, 1):
        print(f"\n{i}. Creating buyer: {buyer['name']}")
        print(f"   Phone: {buyer['phone_number']}")
        
        try:
            response = requests.post(
                f"{base_url}/buyers/",
                json={
                    "name": buyer["name"],
                    "phone_number": buyer["phone_number"],
                    "password": buyer["password"]
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                print(f"   ✅ SUCCESS - Buyer created")
                buyer_data = response.json()
                buyer['uid'] = buyer_data.get('uid')
                print(f"   UID: {buyer['uid']}")
            elif response.status_code == 400:
                print(f"   ⚠️  EXISTS - Buyer already exists")
            else:
                print(f"   ❌ ERROR - {response.status_code}")
                if response.status_code == 422:
                    error = response.json()
                    print(f"   Details: {error.get('detail', 'Unknown error')}")
                    
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
    
    print("\nCreating Test Sellers")
    print("=" * 50)
    
    for i, seller in enumerate(sellers, 1):
        print(f"\n{i}. Creating seller: {seller['name']}")
        print(f"   Phone: {seller['phone_number']}")
        print(f"   Location: {seller['location']}")
        
        try:
            response = requests.post(
                f"{base_url}/sellers/",
                json={
                    "name": seller["name"],
                    "phone_number": seller["phone_number"],
                    "password": seller["password"],
                    "location": seller["location"]
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                print(f"   ✅ SUCCESS - Seller created")
                seller_data = response.json()
                seller['uid'] = seller_data.get('uid')
                print(f"   UID: {seller['uid']}")
            elif response.status_code == 400:
                print(f"   ⚠️  EXISTS - Seller already exists")
            else:
                print(f"   ❌ ERROR - {response.status_code}")
                if response.status_code == 422:
                    error = response.json()
                    print(f"   Details: {error.get('detail', 'Unknown error')}")
                    
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
    
    print("\n" + "=" * 50)
    print("Test User Creation Complete!")
    
    return buyers, sellers

def print_user_credentials():
    """Print all user credentials for easy reference"""
    
    print("\nBUYER CREDENTIALS")
    print("=" * 50)
    for i, buyer in enumerate(buyers, 1):
        print(f"{i}. Name: {buyer['name']}")
        print(f"   Phone: {buyer['phone_number']}")
        print(f"   Password: {buyer['password']}")
        print(f"   Description: {buyer['description']}")
        if 'uid' in buyer:
            print(f"   UID: {buyer['uid']}")
        print()
    
    print("SELLER CREDENTIALS")
    print("=" * 50)
    for i, seller in enumerate(sellers, 1):
        print(f"{i}. Name: {seller['name']}")
        print(f"   Phone: {seller['phone_number']}")
        print(f"   Password: {seller['password']}")
        print(f"   Location: {seller['location']}")
        print(f"   Description: {seller['description']}")
        if 'uid' in seller:
            print(f"   UID: {seller['uid']}")
        print()

if __name__ == "__main__":
    # Create the users
    buyers_list, sellers_list = create_test_users()
    
    # Print credentials
    print_user_credentials()
