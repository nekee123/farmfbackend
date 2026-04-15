import requests
import json

# Test seller phone number validation
base_url = "http://localhost:8000"

# Test cases
test_cases = [
    # Valid phone numbers (should pass)
    {"phone": "09750556999", "expected_status": [201, 400], "description": "Valid format - 11 digits starting with 09"},
    {"phone": "09123456789", "expected_status": [201, 400], "description": "Valid format - 11 digits starting with 09"},
    
    # Invalid phone numbers (should fail)
    {"phone": "+639750556999", "expected_status": 422, "description": "Invalid - starts with +63"},
    {"phone": "0975055699", "expected_status": 422, "description": "Invalid - only 10 digits"},
    {"phone": "097505569999", "expected_status": 422, "description": "Invalid - 12 digits"},
    {"phone": "12345678901", "expected_status": 422, "description": "Invalid - doesn't start with 09"},
    {"phone": "0975055699a", "expected_status": 422, "description": "Invalid - contains letter"},
    {"phone": "0975-055-699", "expected_status": 422, "description": "Invalid - contains dashes"},
]

print("Testing Seller Phone Number Validation")
print("=" * 50)

for i, test_case in enumerate(test_cases, 1):
    phone = test_case["phone"]
    expected_status = test_case["expected_status"]
    description = test_case["description"]
    
    print(f"\nTest {i}: {description}")
    print(f"Phone: {phone}")
    
    # Test seller registration
    seller_data = {
        "name": "Test Seller",
        "phone_number": phone,
        "password": "testpass123",
        "location": "Test Location"
    }
    
    try:
        response = requests.post(
            f"{base_url}/sellers/",
            json=seller_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if isinstance(expected_status, list):
            if response.status_code in expected_status:
                print("✅ PASS - Status code matches expectation")
            else:
                print(f"❌ FAIL - Expected one of {expected_status}, got {response.status_code}")
                if response.status_code == 422:
                    error_data = response.json()
                    print(f"Error: {error_data.get('detail', 'Unknown error')}")
        else:
            if response.status_code == expected_status:
                print("✅ PASS - Status code matches expectation")
            else:
                print(f"❌ FAIL - Expected {expected_status}, got {response.status_code}")
                if response.status_code == 422:
                    error_data = response.json()
                    print(f"Error: {error_data.get('detail', 'Unknown error')}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - Make sure the server is running")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("Testing Complete!")
