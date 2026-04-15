## How to Use Cart with Buyer UID

### 1. Navigate to Cart with Buyer UID

```dart
// Navigate to cart with specific buyer UID
Navigator.pushNamed(
  context,
  '/cart',
  arguments: 'your-buyer-uid-here',
);
```

### 2. Example from Product Screen

```dart
class ProductDetailScreen extends StatelessWidget {
  final String productUid;
  final String buyerUid;
  
  const ProductDetailScreen({
    super.key,
    required this.productUid,
    required this.buyerUid,
  });

  void addToCart() {
    final cartService = CartService();
    cartService.setBuyerUid(buyerUid);
    
    cartService.addToCart(
      buyerUid: buyerUid,
      productUid: productUid,
      quantity: 1,
      priceAtTime: 25.00,
    );
  }

  void goToCart() {
    Navigator.pushNamed(
      context,
      '/cart',
      arguments: buyerUid,
    );
  }
}
```

### 3. From Dashboard

```dart
class ConsumerDashboardScreen extends StatelessWidget {
  void navigateToCart(BuildContext context, String buyerUid) {
    Navigator.pushNamed(
      context,
      '/cart',
      arguments: buyerUid,
    );
  }
}
```

### 4. Test with Default UID

For testing, you can navigate without arguments (uses default '12345'):

```dart
Navigator.pushNamed(context, '/cart');
```

### 5. CartService Usage

```dart
final cartService = CartService();

// Set buyer UID once
cartService.setBuyerUid('your-buyer-uid');

// All subsequent calls will use this buyer UID
final items = await cartService.getCartItems();
final summary = await cartService.getCartSummary();
```

### API Endpoints Now Work:

- `GET /cart/?buyer_uid=12345` ✅
- `GET /cart/summary?buyer_uid=12345` ✅  
- `POST /cart/items` (with buyer_uid in body) ✅
- `PUT /cart/items/{uid}?buyer_uid=12345` ✅
- `DELETE /cart/items/{uid}?buyer_uid=12345` ✅
- `DELETE /cart/?buyer_uid=12345` ✅
