import requests
import json

base_url = "http://localhost:8000"

print("🔐 Admin Account Information")
print("=" * 50)

print("1. Trying to login with default admin credentials...")
admin_credentials = {
    "username": "09876543211",
    "password": "adminpass123"
}

try:
    response = requests.post(f"{base_url}/api/admin/login", json=admin_credentials)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        admin_data = response.json()
        print("   ✅ Default admin account exists!")
        print(f"   Admin UID: {admin_data.get('uid')}")
        print(f"   Username: {admin_data.get('username')}")
        print(f"   Role: {admin_data.get('role')}")
        print(f"   Access Token: {admin_data.get('access_token')[:50]}...")
    else:
        print(f"   ❌ Login failed: {response.text}")
        print("\n2. Creating default admin account...")
        
        # Try to create admin
        create_admin_data = {
            "username": "superadmin",
            "password": "adminpass123",
            "role": "super_admin",
            "email": "admin@farmfresh.com",
            "full_name": "Super Administrator"
        }
        
        try:
            create_response = requests.post(f"{base_url}/api/admin/register", json=create_admin_data)
            print(f"   Create Status: {create_response.status_code}")
            
            if create_response.status_code == 201:
                print("   ✅ Admin account created successfully!")
                created_admin = create_response.json()
                print(f"   Admin UID: {created_admin.get('uid')}")
            else:
                print(f"   ❌ Create failed: {create_response.text}")
        except Exception as e:
            print(f"   Exception: {e}")
            
except Exception as e:
    print(f"   Exception: {e}")

print("\n" + "=" * 50)
print("🔐 Default Admin Credentials:")
print("Username: superadmin")
print("Password: adminpass123")
print("Role: super_admin")
print("\n🌐 Admin Panel: http://localhost:8000/api/admin/docs")
print("📋 API Documentation: http://localhost:8000/docs")
