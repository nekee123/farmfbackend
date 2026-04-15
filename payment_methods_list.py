# Payment Methods - Backend vs Frontend Mapping

## Backend Payment Methods (Database Format)
The backend stores payment methods as comma-separated strings:

### Database Values:
- `"CASH_ON_DELIVERY"` 
- `"MEET_UP_CASH_ON_PICKUP"`
- `"CASH_ON_DELIVERY,MEET_UP_CASH_ON_PICKUP"` (both)

## Frontend Payment Methods (User-Friendly Format)
Your frontend likely displays user-friendly names:

### Frontend Display Names:
- `"Cash on Delivery"`
- `"Meet Up / Cash on Pick-up"`

## Conversion Mapping

### Backend to Frontend:
```python
payment_mapping = {
    "CASH_ON_DELIVERY": "Cash on Delivery",
    "MEET_UP_CASH_ON_PICKUP": "Meet Up / Cash on Pick-up"
}
```

### Frontend to Backend:
```python
reverse_payment_mapping = {
    "Cash on Delivery": "CASH_ON_DELIVERY",
    "Meet Up / Cash on Pick-up": "MEET_UP_CASH_ON_PICKUP"
}
```

## API Usage Examples

### Creating Product (Frontend to Backend):
```javascript
// Frontend sends user-friendly names
{
  "name": "Mango",
  "price": 50,
  "payment_methods": "Cash on Delivery"  // User-friendly
}

// Backend converts to database format
{
  "name": "Mango", 
  "price": 50,
  "payment_methods": "CASH_ON_DELIVERY"  // Database format
}
```

### Multiple Payment Methods:
```javascript
// Frontend selection
["Cash on Delivery", "Meet Up / Cash on Pick-up"]

// Backend storage
"CASH_ON_DELIVERY,MEET_UP_CASH_ON_PICKUP"
```

## Complete Payment Method List

### Supported Payment Methods:
1. **Cash on Delivery**
   - Backend: `CASH_ON_DELIVERY`
   - Description: Pay when product is delivered

2. **Meet Up / Cash on Pick-up**
   - Backend: `MEET_UP_CASH_ON_PICKUP`
   - Description: Pay when picking up product

### Default:
- If no payment method specified, defaults to: `"CASH_ON_DELIVERY,MEET_UP_CASH_ON_PICKUP"`

## Frontend Implementation

### Dropdown Options:
```javascript
const paymentOptions = [
  { value: "Cash on Delivery", label: "Cash on Delivery" },
  { value: "Meet Up / Cash on Pick-up", label: "Meet Up / Cash on Pick-up" }
];
```

### Multi-select Options:
```javascript
const paymentMethods = [
  "Cash on Delivery",
  "Meet Up / Cash on Pick-up"
];
```

### Conversion Function:
```javascript
function convertToBackendFormat(frontendMethods) {
  const mapping = {
    "Cash on Delivery": "CASH_ON_DELIVERY",
    "Meet Up / Cash on Pick-up": "MEET_UP_CASH_ON_PICKUP"
  };
  
  if (Array.isArray(frontendMethods)) {
    return frontendMethods.map(method => mapping[method]).join(',');
  }
  return mapping[frontendMethods] || "CASH_ON_DELIVERY";
}

function convertToFrontendFormat(backendMethods) {
  const mapping = {
    "CASH_ON_DELIVERY": "Cash on Delivery",
    "MEET_UP_CASH_ON_PICKUP": "Meet Up / Cash on Pick-up"
  };
  
  return backendMethods.split(',').map(method => mapping[method.trim()]);
}
```

## Testing

### Test Product Creation:
```javascript
const testProduct = {
  "name": "Test Product",
  "type": "Fruits",
  "price": 50,
  "quantity": 5,
  "description": "Test payment methods",
  "payment_methods": "Cash on Delivery",  // User-friendly
  "seller_uid": "your-seller-uid",
  "seller_name": "Your Name"
};
```

### Expected Backend Storage:
```json
{
  "payment_methods": "CASH_ON_DELIVERY"
}
```

## Summary

**Frontend should use:**
- `"Cash on Delivery"`
- `"Meet Up / Cash on Pick-up"`

**Backend stores as:**
- `"CASH_ON_DELIVERY"`
- `"MEET_UP_CASH_ON_PICKUP"`
- `"CASH_ON_DELIVERY,MEET_UP_CASH_ON_PICKUP"` (both)
