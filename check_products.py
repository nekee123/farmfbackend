import requests

def check_products():
    """Check what payment methods are actually in the database"""
    response = requests.get("http://localhost:8000/products/")
    if response.status_code == 200:
        products = response.json()
        print("Products and their payment methods:")
        for product in products:
            print(f"Product: {product['name']}")
            print(f"  UID: {product['uid']}")
            print(f"  Payment Methods: '{product['payment_methods']}'")
            print(f"  Length: {len(product['payment_methods'])}")
            print(f"  Repr: {repr(product['payment_methods'])}")
            print()
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    check_products()
