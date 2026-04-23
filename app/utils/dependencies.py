from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models import User, UserRole
from .security import decode_access_token
from neo4j import exceptions as neo4j_exceptions
import time

security = HTTPBearer()


def _retry_get_or_none(model_class, **kwargs):
    """Small retry wrapper around model_class.nodes.get_or_none for transient DB errors."""
    attempts = 3
    backoff = 0.5
    last_exc = None
    for attempt in range(attempts):
        try:
            node = model_class.nodes.get_or_none(**kwargs)
            last_exc = None
            return node
        except neo4j_exceptions.ServiceUnavailable as e:
            last_exc = e
            time.sleep(backoff * (attempt + 1))
    # If we got here, raise a HTTPException to be handled by caller context
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Database unavailable, please try again later") from last_exc


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        uid: str = payload.get("sub")
        
        if uid is None:
            raise credentials_exception
        
        user = _retry_get_or_none(User, uid=uid)
        if user is None:
            raise credentials_exception
        
        return user
    except (ValueError, Exception):
        raise credentials_exception


def admin_only(current_user: User = Depends(get_current_user)) -> User:
    """Check if user is an admin"""
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action (Admin only)"
        )
    return current_user


def seller_only(current_user: User = Depends(get_current_user)) -> User:
    """Check if user is a seller"""
    if current_user.role != UserRole.SELLER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action (Seller only)"
        )
    return current_user


def buyer_only(current_user: User = Depends(get_current_user)) -> User:
    """Check if user is a buyer"""
    if current_user.role != UserRole.BUYER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action (Buyer only)"
        )
    return current_user


def seller_or_admin_only(current_user: User = Depends(get_current_user)) -> User:
    """Check if user is a seller or admin"""
    if current_user.role not in [UserRole.SELLER.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action (Seller or Admin only)"
        )
    return current_user
