"""
Authentication Pydantic schemas
"""
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """JWT token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data schema."""
    user_id: Optional[str] = None
    email: Optional[str] = None


class RefreshToken(BaseModel):
    """Refresh token request schema."""
    refresh_token: str


class PasswordReset(BaseModel):
    """Password reset request schema."""
    email: str


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""
    token: str
    new_password: str