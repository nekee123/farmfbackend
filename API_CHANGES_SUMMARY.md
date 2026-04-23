# API Changes Summary - Unified User Model with RBAC

## 🎯 Overview
The backend has been refactored from separate Buyer/Seller/Admin models to a **unified User model** with Role-Based Access Control (RBAC). This is a major architectural change that affects authentication, user management, and all API endpoints.

---

## 🔄 Major Changes

### 1. **Unified User Model**
**Old System:**
- Separate models: `Buyer`, `Seller`, `Admin`
- Phone number authentication for buyers/sellers
- Username authentication for admins
- Profile pictures stored in user models

**New System:**
- Single `User` model with `role` field (buyer/seller/admin)
- **Phone number** as the primary identifier for all users
- **Removed email and profile_picture fields**
- Role-based access control (RBAC)

---

## 📝 Authentication Changes

### Registration Endpoint
**Endpoint:** `POST /api/auth/register`

**Old Endpoints:**
- `POST /api/buyers/` (for buyers)
- `POST /api/sellers/` (for sellers)
- `POST /api/admin/register` (for admins)

**New Request Body:**
```json
{
  "phone_number": "09123456789",
  "password": "password123",
  "full_name": "John Doe",
  "location": "City",
  "role": "buyer"  // Optional: "buyer", "seller", or "admin" (default: "buyer")
}
```

**Response:**
```json
{
  "uid": "user-uid",
  "phone_number": "09123456789",
  "full_name": "John Doe",
  "location": "City",
  "role": "buyer",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

---

### Login Endpoint
**Endpoint:** `POST /api/auth/login`

**Old Endpoints:**
- `POST /api/buyers/login` (buyers used phone_number)
- `POST /api/sellers/login` (sellers used phone_number)
- `POST /api/admin/login` (admins used username)

**New Request Body:**
```json
{
  "phone_number": "09123456789",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "buyer",
  "user_id": "user-uid"
}
```

---

## 🔐 JWT Token Changes
**Old Token Payload:**
- Contained user-specific fields depending on user type

**New Token Payload:**
```json
{
  "sub": "user-uid",      // User ID
  "role": "buyer",        // User role: "buyer", "seller", or "admin"
  "exp": 1234567890       // Expiration time
}
```

---

## 🛡️ RBAC Protection

All protected endpoints now require JWT tokens in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

### Role-Based Access:
- **buyer_only**: Only buyers can access
- **seller_only**: Only sellers can access
- **admin_only**: Only admins can access
- **get_current_user**: Any authenticated user can access

---

## 📦 Product API Changes

### Create Product
**Endpoint:** `POST /api/products/`
**Protection:** `seller_only` (Only sellers can create products)

**Old Request Body:**
```json
{
  "seller_uid": "seller-uid",
  "seller_name": "Seller Name",
  "name": "Product Name",
  "type": "Fruits",
  "price": 50,
  "quantity": 10,
  "description": "...",
  "payment_methods": "CASH_ON_DELIVERY,MEET_UP_CASH_ON_PICKUP"
}
```

**New Request Body:**
```json
{
  "name": "Product Name",
  "type": "Fruits",
  "price": 50,
  "quantity": 10,
  "description": "...",
  "payment_methods": "CASH_ON_DELIVERY,MEET_UP_CASH_ON_PICKUP"
}
```
**Note:** `seller_uid` is now automatically extracted from the JWT token.

**Headers:**
```
Authorization: Bearer <seller_token>
```

---

### Update/Delete Product
**Endpoints:**
- `PATCH /api/products/{uid}` - Update product
- `DELETE /api/products/{uid}` - Delete product
**Protection:** `seller_only` (Only the seller who created the product can update/delete)

---

## 🛒 Order API Changes

### Create Order
**Endpoint:** `POST /api/orders/`
**Protection:** `buyer_only` (Only buyers can place orders)

**Old Request Body:**
```json
{
  "buyer_uid": "buyer-uid",
  "buyer_name": "Buyer Name",
  "seller_uid": "seller-uid",
  "seller_name": "Seller Name",
  "farm_product_uid": "product-uid",
  "farm_product_name": "Product Name",
  "quantity": 2,
  "payment_method": "Cash on Delivery",
  "total_price": 100
}
```

**New Request Body:**
```json
{
  "farm_product_uid": "product-uid",
  "quantity": 2,
  "payment_method": "Cash on Delivery"  // or "Meet Up / Cash on Pick-up"
}
```
**Note:** `buyer_uid` is now automatically extracted from the JWT token.

**Headers:**
```
Authorization: Bearer <buyer_token>
```

---

### Get Orders
**New Endpoint:** `GET /api/orders/my-orders`
**Protection:** `get_current_user`
- Buyers see their placed orders
- Sellers see orders they fulfilled

**Endpoint:** `GET /api/orders/`
**Protection:** `admin_only` (Only admins can see all orders)

---

### Update Order Status
**Endpoint:** `PATCH /api/orders/{uid}/status`
**Protection:** `seller_only` (Only sellers can update order status)

**Request Body:**
```json
{
  "order_status": "Delivered"  // Options: "Pending", "Confirmed", "Cancelled", "Delivered"
}
```

---

## 👤 User Profile Changes

### Removed Fields:
- ✗ `email` - No longer used
- ✗ `profile_picture` - No longer stored in user model

### User Response Fields:
```json
{
  "uid": "user-uid",
  "phone_number": "09123456789",
  "full_name": "John Doe",
  "location": "City",
  "role": "buyer",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "last_login": "2024-01-01T00:00:00"
}
```

---

## 🚫 Deprecated Endpoints

**Removed Endpoints (Do Not Use):**
- `POST /api/buyers/` - Use `POST /api/auth/register` with `role: "buyer"`
- `POST /api/sellers/` - Use `POST /api/auth/register` with `role: "seller"`
- `POST /api/buyers/login` - Use `POST /api/auth/login`
- `POST /api/sellers/login` - Use `POST /api/auth/login`
- `POST /api/admin/login` - Use `POST /api/auth/login` with admin credentials
- `GET /api/buyers/` - Deprecated
- `GET /api/sellers/` - Deprecated
- `GET /api/buyers/{uid}` - Deprecated
- `GET /api/sellers/{uid}` - Deprecated

---

## 🔍 Search API Changes

**Endpoint:** `GET /search`

**Query Parameters:**
- `query`: Search term
- `search_type`: "products", "sellers", or "buyers"

**Updated for User Model:**
- Sellers search now queries `User` nodes with `role: "seller"`
- Buyers search now queries `User` nodes with `role: "buyer"`

---

## 📝 Review API Changes

### Review Response (Removed Fields)
**Old Response:**
```json
{
  "buyer_profile_picture": "base64_or_url",
  ...
}
```

**New Response:**
```json
{
  "uid": "review-uid",
  "buyer_uid": "buyer-uid",
  "buyer_name": "Buyer Name",
  "seller_uid": "seller-uid",
  ...
}
```
**Note:** `buyer_profile_picture` field removed.

---

## 🎯 Migration Guide for Frontend

### 1. **Update Authentication Flow**
- Remove separate buyer/seller login screens
- Use single login form with phone number and password
- Store JWT token and user role in app state
- Include JWT token in all API request headers

### 2. **Update Registration Flow**
- Use single registration form
- Add role selection (optional, defaults to "buyer")
- Phone number is now required and unique
- Email field removed
- Profile picture field removed

### 3. **Update API Calls**
- Remove `seller_uid` and `buyer_uid` from request bodies
- Add `Authorization: Bearer <token>` header to all protected calls
- Use `/api/auth/login` and `/api/auth/register` instead of role-specific endpoints

### 4. **Handle Role-Based Access**
- Check user role from JWT token or `/api/auth/me` endpoint
- Hide/show features based on user role
- Handle 403 Forbidden errors when user doesn't have required role

### 5. **Update User Profile Display**
- Remove email field from user profiles
- Remove profile picture field from user profiles
- Display phone number as primary identifier

---

## 🧪 Testing

Use the provided test script to verify the changes:
```bash
python test_unified_auth.py
```

This will test:
- User registration for all roles
- User login for all roles
- RBAC protection on endpoints
- JWT token generation and validation

---

## 📞 Contact

If you have any questions or need clarification on these changes, please refer to the backend team.

---

## 🚀 Summary

**Key Takeaways:**
1. **Unified Authentication:** Single login/register for all user types
2. **Phone-Based:** Phone number is the primary identifier (no email)
3. **No Profile Pictures:** Profile picture field removed from user model
4. **RBAC:** Role-based access control on all protected endpoints
5. **JWT Tokens:** Include user_id and role in payload
6. **Automatic User Context:** User ID extracted from token, not sent in request body

**Version:** 2.0.0
**Breaking Changes:** Yes - Frontend must be updated to work with new authentication system
