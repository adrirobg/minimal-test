"""
Authentication endpoints for user registration, login, and token management
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user, get_refresh_token_user
from app.core.security import (
    verify_password, get_password_hash, create_token_response,
    verify_password_reset_token, generate_password_reset_token
)
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserInDB
from app.schemas.auth import Token, RefreshToken, PasswordReset, PasswordResetConfirm
from app.schemas.common import MessageResponse


router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Register a new user account.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If email is already registered
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address is already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        is_active=user_data.is_active,
        is_superuser=user_data.is_superuser,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserResponse.model_validate(new_user)


@router.post("/login", response_model=Token)
async def login_user(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> Token:
    """
    Authenticate user and return access/refresh tokens.
    
    Args:
        user_credentials: User login credentials
        db: Database session
        
    Returns:
        JWT tokens
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Get user by email
    result = await db.execute(select(User).where(User.email == user_credentials.email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Create tokens
    token_response = create_token_response(str(user.id), user.email)
    
    return Token(**token_response)


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    current_user: UserInDB = Depends(get_refresh_token_user)
) -> Token:
    """
    Refresh access token using refresh token.
    
    Args:
        current_user: User from valid refresh token
        
    Returns:
        New JWT tokens
    """
    # Create new tokens
    token_response = create_token_response(str(current_user.id), current_user.email)
    
    return Token(**token_response)


@router.post("/logout", response_model=MessageResponse)
async def logout_user(
    current_user: UserInDB = Depends(get_current_user)
) -> MessageResponse:
    """
    Logout user (client should discard tokens).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    # In a production system, you might want to blacklist the tokens
    # For now, we rely on client-side token removal
    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserInDB = Depends(get_current_user)
) -> UserResponse:
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return UserResponse.model_validate(current_user)


@router.post("/password-reset", response_model=MessageResponse)
async def request_password_reset(
    password_reset: PasswordReset,
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Request password reset token.
    
    Args:
        password_reset: Password reset request data
        db: Database session
        
    Returns:
        Success message
    """
    # Check if user exists
    result = await db.execute(select(User).where(User.email == password_reset.email))
    user = result.scalar_one_or_none()
    
    if not user:
        # Don't reveal whether email exists or not for security
        return MessageResponse(
            message="If the email exists, a password reset link has been sent"
        )
    
    if not user.is_active:
        return MessageResponse(
            message="If the email exists, a password reset link has been sent"
        )
    
    # Generate password reset token
    reset_token = generate_password_reset_token(user.email)
    
    # In a real application, you would send an email with the reset token
    # For now, we just return a success message
    # TODO: Implement email sending
    
    return MessageResponse(
        message="If the email exists, a password reset link has been sent"
    )


@router.post("/password-reset/confirm", response_model=MessageResponse)
async def confirm_password_reset(
    password_reset_confirm: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Confirm password reset and update password.
    
    Args:
        password_reset_confirm: Password reset confirmation data
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If reset token is invalid or expired
    """
    # Verify reset token
    email = verify_password_reset_token(password_reset_confirm.token)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token"
        )
    
    # Get user by email
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token"
        )
    
    # Update password
    hashed_password = get_password_hash(password_reset_confirm.new_password)
    user.password_hash = hashed_password
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return MessageResponse(message="Password has been reset successfully")


@router.post("/verify-token", response_model=UserResponse)
async def verify_token_endpoint(
    current_user: UserInDB = Depends(get_current_user)
) -> UserResponse:
    """
    Verify if current token is valid and return user info.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information if token is valid
    """
    return UserResponse.model_validate(current_user)