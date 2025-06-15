"""
User management endpoints
"""
import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.deps import get_db, get_current_user, get_current_active_superuser
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserInDB, UserProfile
from app.schemas.common import PaginatedResponse, MessageResponse


router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: UserInDB = Depends(get_current_user)
) -> UserProfile:
    """
    Get current user profile.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User profile information
    """
    return UserProfile.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Update current user information.
    
    Args:
        user_update: User update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user information
    """
    # Get user from database
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "password" and value:
            # Hash new password
            user.password_hash = get_password_hash(value)
        elif field == "email" and value:
            # Check if email is already taken
            existing = await db.execute(
                select(User).where(User.email == value, User.id != user.id)
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email address is already registered"
                )
            user.email = value
        elif hasattr(user, field):
            setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.delete("/me", response_model=MessageResponse)
async def delete_current_user(
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Delete current user account.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    # Get user from database
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Soft delete by deactivating account
    user.is_active = False
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return MessageResponse(message="User account has been deactivated")


# Admin endpoints (superuser only)
@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    current_user: UserInDB = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
) -> PaginatedResponse[UserResponse]:
    """
    List all users (admin only).
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Search term for email or name
        current_user: Current superuser
        db: Database session
        
    Returns:
        Paginated list of users
    """
    # Build query
    query = select(User)
    
    if search:
        search_filter = User.email.ilike(f"%{search}%")
        if search:
            search_filter = search_filter | User.full_name.ilike(f"%{search}%")
        query = query.where(search_filter)
    
    # Get total count
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    result = await db.execute(query)
    users = result.scalars().all()
    
    return PaginatedResponse[UserResponse](
        items=[UserResponse.model_validate(user) for user in users],
        total=total,
        limit=limit,
        offset=skip,
        has_next=skip + limit < total,
        has_previous=skip > 0
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    current_user: UserInDB = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Get user by ID (admin only).
    
    Args:
        user_id: User ID
        current_user: Current superuser
        db: Database session
        
    Returns:
        User information
        
    Raises:
        HTTPException: If user not found
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Update user by ID (admin only).
    
    Args:
        user_id: User ID
        user_update: User update data
        current_user: Current superuser
        db: Database session
        
    Returns:
        Updated user information
        
    Raises:
        HTTPException: If user not found
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "password" and value:
            user.password_hash = get_password_hash(value)
        elif field == "email" and value:
            # Check if email is already taken
            existing = await db.execute(
                select(User).where(User.email == value, User.id != user.id)
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email address is already registered"
                )
            user.email = value
        elif hasattr(user, field):
            setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: uuid.UUID,
    current_user: UserInDB = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Delete user by ID (admin only).
    
    Args:
        user_id: User ID
        current_user: Current superuser
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If user not found
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Soft delete by deactivating
    user.is_active = False
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    
    return MessageResponse(message="User has been deactivated")