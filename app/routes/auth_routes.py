from fastapi import APIRouter, status, Depends
from ..schemas import UserCreate, UserLogin, UserResponse, UserToken, UserUpdate
from ..controllers import AuthController
from fastapi import APIRouter
from app.utils.sms import send_otp_sms
from app.schemas.user import OTPVerify, ResendOTP
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate):
    """
    Register a new user with an optional role (default is 'buyer')
    """
    return AuthController.register(user_data)


@router.post("/login", status_code=status.HTTP_200_OK)
def login(login_data: UserLogin):
    """
    Unified login for all users (buyer, seller, admin) using email and password
    """
    return AuthController.login(login_data)


@router.put("/profile", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_profile(user_data: UserUpdate):
    """
    Update user profile
    """
    return AuthController.update_profile(user_data)



@router.post("/verify-otp")
def verify_otp(data: OTPVerify):
    return AuthController.verify_otp(data)

@router.post("/resend-otp")
def resend_otp(data: ResendOTP):
    return AuthController.resend_otp(data)