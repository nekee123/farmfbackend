import requests

def debug_payment_methods():
    """Debug payment method comparison"""
    response = requests.get("http://localhost:8000/products/a3c871f40c2a4ff9afec5100114a1cbb")
    if response.status_code == 200:
        product = response.json()
        db_payment = product['payment_methods']
        frontend_payment = "Meet Up / Cash on Pick-up"
        
        print(f"Database payment: '{db_payment}'")
        print(f"Frontend payment: '{frontend_payment}'")
        print(f"Database length: {len(db_payment)}")
        print(f"Frontend length: {len(frontend_payment)}")
        print(f"Database repr: {repr(db_payment)}")
        print(f"Frontend repr: {repr(frontend_payment)}")
        print(f"Are equal? {db_payment == frontend_payment}")
        print(f"Database chars: {[ord(c) for c in db_payment]}")
        print(f"Frontend chars: {[ord(c) for c in frontend_payment]}")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    debug_payment_methods()
