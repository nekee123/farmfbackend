import requests
import json

base_url = "http://localhost:8000"

print("🔐 Creating Admin Account")
print("=" * 50)

admin_data = {
    "phone_number": "09876543211",
    "password": "admin123",
    "full_name": "Administrator",
    "location": "Admin Office",
    "role": "admin"
}

try:
    response = requests.post(f"{base_url}/api/auth/register", json=admin_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        print("✅ Admin account created successfully!")
        admin = response.json()
        print(f"UID: {admin['uid']}")
        print(f"Phone: {admin['phone_number']}")
        print(f"Full Name: {admin['full_name']}")
        print(f"Role: {admin['role']}")
    else:
        print(f"❌ Failed: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("🔐 Admin Login Credentials:")
print("Phone Number: 09876543211")
print("Password: admin123")
print("Role: admin")
print("\n🌐 Login at: POST /api/auth/login")
