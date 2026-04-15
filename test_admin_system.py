import requests
import json

base_url = "http://localhost:8000"

print("🧑‍⚖️ Creating Admin User")
print("=" * 50)

# Create super admin
admin_data = {
    "username": "superadmin",
    "email": "admin@farmfresh.com",
    "full_name": "Super Administrator",
    "role": "super_admin",
    "is_active": True,
    "permissions": ["manage_users", "manage_products", "manage_orders", "system_settings"],
    "password": "adminpass123",
    "confirm_password": "adminpass123"
}

print(f"Admin data: {json.dumps(admin_data, indent=2)}")

try:
    response = requests.post(
        f"{base_url}/admin/register",
        json=admin_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        print("✅ SUCCESS - Admin created!")
        admin_response = response.json()
        print(f"UID: {admin_response.get('uid')}")
        print(f"Username: {admin_response.get('username')}")
        print(f"Role: {admin_response.get('role')}")
        print(f"Permissions: {admin_response.get('permissions')}")
    elif response.status_code == 422:
        print("⚠️  VALIDATION ERROR")
        error = response.json()
        print(f"Error: {error.get('detail', 'Unknown error')}")
    else:
        print(f"❌ ERROR - {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 50)
print("🔑 Testing Admin Login")

# Test admin login
login_data = {
    "username": "superadmin",
    "password": "adminpass123"
}

print(f"Login data: {json.dumps(login_data, indent=2)}")

try:
    response = requests.post(
        f"{base_url}/admin/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS - Admin login successful!")
        login_response = response.json()
        access_token = login_response.get('access_token')
        admin_info = login_response.get('admin')
        
        print(f"Access Token: {access_token[:50]}...")
        print(f"Admin: {admin_info.get('full_name')} ({admin_info.get('role')})")
        
        # Store token for next tests
        admin_token = access_token
        
        print("\n" + "=" * 50)
        print("📊 Testing Dashboard Stats")
        
        # Test dashboard stats
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        try:
            response = requests.get(
                f"{base_url}/admin/dashboard/stats",
                headers=headers
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS - Dashboard stats retrieved!")
                stats = response.json()
                print(f"Total Users: {stats.get('total_users')}")
                print(f"Total Buyers: {stats.get('total_buyers')}")
                print(f"Total Sellers: {stats.get('total_sellers')}")
                print(f"Total Products: {stats.get('total_products')}")
                print(f"Total Orders: {stats.get('total_orders')}")
                print(f"Recent Registrations: {stats.get('recent_registrations')}")
            else:
                print(f"❌ ERROR - {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"Exception: {e}")
            
    else:
        print(f"❌ ERROR - {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "=" * 50)
print("✅ Admin System Ready!")
print("\n📋 Admin Features Available:")
print("1. 🧑‍⚖️ User Management - Approve/block/ban users")
print("2. 🛒 Product Management - Approve/remove/flag products")
print("3. 📦 Order Management - Handle disputes and refunds")
print("4. 📊 Dashboard & Reports - Monitor platform activity")
print("5. ⚙️ System Settings - Configure platform policies")
print("\n🔐 Admin Login Credentials:")
print("Username: superadmin")
print("Password: adminpass123")
print("Role: super_admin")
print("\n🌐 Access Admin Panel: http://localhost:8000/admin/docs")
