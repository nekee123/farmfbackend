from fastapi import HTTPException, status
from ..models import Buyer, Seller
from ..schemas import Token, BuyerLogin, SellerLogin
from ..utils.security import verify_password, create_access_token
from ..utils.dependencies import _retry_get_or_none


class AuthController:
    """Controller for authentication operations"""
    
    @staticmethod
    def login_buyer(login_data: BuyerLogin) -> Token:
        """Authenticate buyer and return JWT token"""
        buyer = _retry_get_or_none(Buyer, phone_number=login_data.phone_number)
        
        if not buyer or not verify_password(login_data.password, buyer.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect phone number or password"
            )
        
        # Create access token
        access_token = create_access_token(
            data={
                "uid": buyer.uid,
                "phone_number": buyer.phone_number,
                "user_type": "buyer"
            }
        )
        
        return Token(access_token=access_token)
    
    @staticmethod
    def login_seller(login_data: SellerLogin) -> Token:
        """Authenticate seller and return JWT token"""
        seller = _retry_get_or_none(Seller, phone_number=login_data.phone_number)
        
        if not seller or not verify_password(login_data.password, seller.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect phone number or password"
            )
        
        # Create access token
        access_token = create_access_token(
            data={
                "uid": seller.uid,
                "phone_number": seller.phone_number,
                "user_type": "seller"
            }
        )
        
        return Token(access_token=access_token)
