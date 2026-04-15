from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    uid: str
    phone_number: str
    user_type: str  # "buyer" or "seller"
