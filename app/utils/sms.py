import requests
from app.config import settings


def format_phone_number(phone_number: str) -> str:
    """
    Convert 09XXXXXXXXX → +639XXXXXXXXX
    """

    if phone_number.startswith("09"):
        return "+63" + phone_number[1:]

    return phone_number


def send_otp_sms(phone_number: str, otp_code: str):
    """
    Send OTP via UniSMS
    """

    url = "https://unismsapi.com/api/sms"

    payload = {
        "recipient": format_phone_number(phone_number),
        "content": f"Your OTP for FarmFresh is: {otp_code}"
    }

    response = requests.post(
        url,
        json=payload,
        auth=(settings.unisms_api_secret, "")  # 👈 IMPORTANT
    )

    return response.json()