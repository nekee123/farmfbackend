from fastapi import HTTPException, status
from ..models import User, UserRole
from ..schemas import UserCreate, UserLogin, UserResponse, UserToken, UserUpdate
from ..utils.security import get_password_hash, verify_password, create_access_token
from ..utils.dependencies import _retry_get_or_none


class AuthController:
    """Controller for unified authentication operations"""
    
    @staticmethod
    def register(user_data: UserCreate) -> UserResponse:
        """Register a new user (buyer, seller, or admin)"""
        # Check if phone_number exists
        existing_user = _retry_get_or_none(User, phone_number=user_data.phone_number)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        
        # Create new user
        new_user = User(
            phone_number=user_data.phone_number,
            password_hash=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            role=user_data.role.value,
            location=user_data.location or "",
            profile_picture=user_data.profile_picture or "",
            is_banned=False,
            category=user_data.category or ""
        ).save()
        
        return UserResponse.from_orm(new_user)

    @staticmethod
    def login(login_data: UserLogin) -> dict:
        """Authenticate user and return unified JWT token with user data"""

        user = _retry_get_or_none(
            User,
            phone_number=login_data.phone_number
        )

        # Check credentials
        if not user or not verify_password(
            login_data.password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect phone number or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # =====================================
        # CHECK IF USER IS BANNED
        # =====================================
        if user.is_banned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been banned"
            )

        # Create access token
        access_token = create_access_token(
            data={
                "sub": user.uid,
                "role": user.role
            }
        )

        # Update last login
        user.update_last_login()

        # Return token + user data
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "uid": user.uid,
                "phone_number": user.phone_number,
                "full_name": user.full_name,
                "role": user.role,
                "location": user.location,
                "profile_picture": user.profile_picture,
                "is_banned": user.is_banned,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            }
        }

    @staticmethod
    def update_profile(user_data: UserUpdate) -> UserResponse:
        """Update user profile"""
        # For now, this is a placeholder - in a real app you'd need authentication
        # to identify which user to update
        # For this demo, we'll just return the data as if it was updated
        # In production, you'd:
        # 1. Get the user from JWT token
        # 2. Update the user node in Neo4j
        # 3. Return the updated user
        
        # This is a simplified version that doesn't actually update the database
        # For a complete implementation, you'd need to:
        # 1. Add authentication dependency to get the current user
        # 2. Fetch the user by uid from the token
        # 3. Update the user's fields
        # 4. Save and return
        
        # For now, we'll return a mock response
        from ..models import User
        user = _retry_get_or_none(User, phone_number=user_data.phone_number)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user_data.full_name:
            user.full_name = user_data.full_name
        if user_data.location:
            user.location = user_data.location
        if user_data.profile_picture:
            user.profile_picture = user_data.profile_picture
        if user_data.password:
            user.password_hash = get_password_hash(user_data.password)
        
        user.update_timestamp()
        user.save()
        
        return UserResponse.from_orm(user)
