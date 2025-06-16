"""
FastAPI dependencies for authentication and database access
"""
import uuid
from typing import Optional, AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_async_session
from app.core.security import verify_token
from app.models.user import User
from app.schemas.user import UserInDB


# OAuth2 scheme for JWT authentication
security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    """
    async for session in get_async_session():
        yield session


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[UserInDB]:
    """
    Get current user from JWT token (optional - returns None if no token).
    
    Args:
        credentials: HTTP Authorization credentials
        db: Database session
        
    Returns:
        User object if authenticated, None otherwise
    """
    if not credentials:
        return None
        
    token = credentials.credentials
    payload = verify_token(token, "access")
    
    if not payload:
        return None
        
    user_id = payload.get("sub")
    if not user_id:
        return None
        
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return None
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        return None
        
    return UserInDB.model_validate(user)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserInDB:
    """
    Get current user from JWT token (required - raises exception if not authenticated).
    
    Args:
        credentials: HTTP Authorization credentials
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    token = credentials.credentials
    payload = verify_token(token, "access")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
        
    return UserInDB.model_validate(user)


async def get_current_active_superuser(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    """
    Get current superuser (admin privileges required).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object with superuser privileges
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def verify_user_ownership(
    resource_user_id: uuid.UUID,
    current_user: UserInDB = Depends(get_current_user)
) -> bool:
    """
    Verify that the current user owns the resource or is a superuser.
    
    Args:
        resource_user_id: User ID of the resource owner
        current_user: Current authenticated user
        
    Returns:
        True if user owns resource or is superuser
        
    Raises:
        HTTPException: If user doesn't own resource and is not superuser
    """
    if current_user.is_superuser or current_user.id == resource_user_id:
        return True
        
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions to access this resource"
    )


class CommonQueryParams:
    """
    Common query parameters for pagination and filtering.
    """
    def __init__(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None
    ):
        self.skip = skip
        self.limit = min(limit, 100)  # Max 100 items per page
        self.search = search


async def get_refresh_token_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserInDB:
    """
    Validate refresh token and return user.
    
    Args:
        credentials: HTTP Authorization credentials with refresh token
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )
        
    token = credentials.credentials
    payload = verify_token(token, "refresh")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
        
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
        )
        
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in refresh token",
        )
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
        
    return UserInDB.model_validate(user)