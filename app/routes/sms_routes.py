from fastapi import APIRouter
from app.utils.sms import send_otp_sms

router = APIRouter()


@router.get("/test-otp")
def test_otp():

    result = send_otp_sms("09975435815")

    return result