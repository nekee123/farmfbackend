# Order System Documentation

## Overview

The FarmFresh Connect order system has been updated with enhanced payment and status management features.

## New Properties

### Order Model Properties

- **payment_method** (required): String with allowed values:
  - `"Cash on Delivery"`
  - `"Meet Up / Cash on Pick-up"`

- **order_status**: String with allowed values:
  - `"Pending"` (default)
  - `"Delivered"`

## API Endpoints

### Create Order
```
POST /orders/
```

**Request Body:**
```json
{
  "buyer_uid": "string",
  "farm_product_uid": "string", 
  "quantity": 1,
  "payment_method": "Cash on Delivery" | "Meet Up / Cash on Pick-up"
}
```

**Validation:**
- `payment_method` is required and must be one of the allowed values
- Returns HTTP 400 for invalid payment methods
- Automatically sets `order_status` to "Pending"

### Update Order Status
```
PATCH /orders/{order_id}/status
```

**Request Body:**
```json
{
  "order_status": "Delivered"
}
```

**Validation:**
- Only allows updating status to "Delivered"
- Prevents changing back to "Pending"
- Returns HTTP 400 for invalid status values
- Returns HTTP 404 if order not found

**Response:**
```json
{
  "message": "Order status updated successfully",
  "order_uid": "string",
  "order_status": "Delivered"
}
```

## Order Response Format

All order responses include the new fields:

```json
{
  "uid": "string",
  "buyer_uid": "string",
  "buyer_name": "string",
  "buyer_contact": "+639750556999",
  "seller_uid": "string", 
  "seller_name": "string",
  "seller_contact": "+639750556998",
  "farm_product_uid": "string",
  "farm_product_name": "string",
  "quantity": 1,
  "total_price": 150.0,
  "order_status": "Pending" | "Delivered",
  "payment_method": "Cash on Delivery" | "Meet Up / Cash on Pick-up",
  "reviewed": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## Business Logic

### Order Creation
1. Validates payment method is one of the allowed values
2. Sets order status to "Pending" automatically
3. Creates order with buyer, seller, and product relationships
4. Reduces product quantity accordingly

### Status Updates
1. Only allows transition from "Pending" to "Delivered"
2. Prevents reverting from "Delivered" back to "Pending"
3. Updates timestamp on status change
4. Returns success confirmation

### Error Handling
- **HTTP 400**: Invalid payment method or status value
- **HTTP 404**: Order not found
- **HTTP 201**: Order created successfully
- **HTTP 200**: Status updated successfully

## Pydantic Models

### OrderCreate
```python
class OrderCreate(BaseModel):
    buyer_uid: str
    farm_product_uid: str
    quantity: int = Field(..., gt=0)
    payment_method: str = Field(..., pattern="^(Cash on Delivery|Meet Up \/ Cash on Pick-up)$")
```

### OrderStatusUpdate
```python
class OrderStatusUpdate(BaseModel):
    order_status: str = Field(..., pattern="^(Delivered)$")
```

### OrderResponse
```python
class OrderResponse(BaseModel):
    # ... all order fields including:
    order_status: str
    payment_method: str
    # ... other fields
```

## Neo4j Cypher Queries

The system uses optimized Cypher queries for:

- Order creation with relationships
- Status updates with validation
- Product quantity management
- Buyer/seller order retrieval

## Testing

Run the test suite to verify functionality:

```bash
python test_order_system.py
```

This tests:
- Order creation with valid payment methods
- Rejection of invalid payment methods
- Status updates to "Delivered"
- Rejection of invalid status updates
