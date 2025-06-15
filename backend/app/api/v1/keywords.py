"""
Keywords management endpoints
"""
import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user
from app.models.keyword import Keyword
from app.models.note import Note
from app.schemas.user import UserInDB
from app.schemas.keyword import (
    KeywordCreate, KeywordUpdate, KeywordResponse,
    KeywordWithNotes, KeywordStats
)
from app.schemas.common import PaginatedResponse, MessageResponse


router = APIRouter()


@router.get("/", response_model=PaginatedResponse[KeywordWithNotes])
async def list_keywords(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    include_stats: bool = Query(False),
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PaginatedResponse[KeywordWithNotes]:
    """
    List user's keywords with optional filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Search term for keyword name
        include_stats: Include usage statistics
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of keywords
    """
    # Build query
    query = select(Keyword).where(Keyword.user_id == current_user.id)
    
    if search:
        query = query.where(Keyword.name.ilike(f"%{search}%"))
    
    # Get total count
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(Keyword.name)
    result = await db.execute(query)
    keywords = result.scalars().all()
    
    # Get notes count for each keyword
    keywords_with_notes = []
    for keyword in keywords:
        # Count associated notes
        from app.models.note import note_keywords
        notes_count_query = (
            select(func.count())
            .select_from(note_keywords)
            .where(note_keywords.c.keyword_id == keyword.id)
        )
        notes_count_result = await db.execute(notes_count_query)
        notes_count = notes_count_result.scalar()
        
        keyword_dict = KeywordWithNotes.model_validate(keyword).model_dump()
        keyword_dict['notes_count'] = notes_count
        keywords_with_notes.append(KeywordWithNotes(**keyword_dict))
    
    return PaginatedResponse[KeywordWithNotes](
        items=keywords_with_notes,
        total=total,
        limit=limit,
        offset=skip,
        has_next=skip + limit < total,
        has_previous=skip > 0
    )


@router.get("/stats", response_model=List[KeywordStats])
async def get_keyword_stats(
    limit: int = Query(10, ge=1, le=50),
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[KeywordStats]:
    """
    Get keyword usage statistics (most used keywords).
    
    Args:
        limit: Maximum number of keywords to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of keywords with usage statistics
    """
    from app.models.note import note_keywords
    
    # Get keywords with note counts, ordered by usage
    query = (
        select(Keyword, func.count(note_keywords.c.note_id).label('notes_count'))
        .outerjoin(note_keywords)
        .where(Keyword.user_id == current_user.id)
        .group_by(Keyword.id)
        .order_by(func.count(note_keywords.c.note_id).desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    keyword_stats = result.all()
    
    # Get recent notes for each keyword
    stats_list = []
    for keyword, notes_count in keyword_stats:
        # Get recent notes for this keyword
        recent_notes_query = (
            select(Note)
            .join(note_keywords)
            .where(
                note_keywords.c.keyword_id == keyword.id,
                Note.user_id == current_user.id
            )
            .order_by(Note.updated_at.desc())
            .limit(3)
        )
        recent_notes_result = await db.execute(recent_notes_query)
        recent_notes = recent_notes_result.scalars().all()
        
        stats = KeywordStats(
            **KeywordResponse.model_validate(keyword).model_dump(),
            notes_count=notes_count,
            recent_notes=[note for note in recent_notes]
        )
        stats_list.append(stats)
    
    return stats_list


@router.post("/", response_model=KeywordResponse, status_code=status.HTTP_201_CREATED)
async def create_keyword(
    keyword_data: KeywordCreate,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> KeywordResponse:
    """
    Create a new keyword.
    
    Args:
        keyword_data: Keyword creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created keyword information
        
    Raises:
        HTTPException: If keyword already exists for user
    """
    # Check if keyword already exists for this user
    existing_result = await db.execute(
        select(Keyword).where(
            Keyword.name == keyword_data.name.lower(),
            Keyword.user_id == current_user.id
        )
    )
    existing_keyword = existing_result.scalar_one_or_none()
    
    if existing_keyword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keyword already exists"
        )
    
    # Create new keyword
    new_keyword = Keyword(
        name=keyword_data.name.lower(),  # Store normalized
        user_id=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_keyword)
    await db.commit()
    await db.refresh(new_keyword)
    
    return KeywordResponse.model_validate(new_keyword)


@router.get("/{keyword_id}", response_model=KeywordStats)
async def get_keyword(
    keyword_id: uuid.UUID,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> KeywordStats:
    """
    Get keyword by ID with statistics.
    
    Args:
        keyword_id: Keyword ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Keyword information with statistics
        
    Raises:
        HTTPException: If keyword not found or doesn't belong to user
    """
    result = await db.execute(
        select(Keyword).where(
            Keyword.id == keyword_id,
            Keyword.user_id == current_user.id
        )
    )
    keyword = result.scalar_one_or_none()
    
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )
    
    # Get notes count and recent notes
    from app.models.note import note_keywords
    
    notes_count_query = (
        select(func.count())
        .select_from(note_keywords)
        .where(note_keywords.c.keyword_id == keyword_id)
    )
    notes_count_result = await db.execute(notes_count_query)
    notes_count = notes_count_result.scalar()
    
    recent_notes_query = (
        select(Note)
        .join(note_keywords)
        .where(
            note_keywords.c.keyword_id == keyword_id,
            Note.user_id == current_user.id
        )
        .order_by(Note.updated_at.desc())
        .limit(5)
    )
    recent_notes_result = await db.execute(recent_notes_query)
    recent_notes = recent_notes_result.scalars().all()
    
    return KeywordStats(
        **KeywordResponse.model_validate(keyword).model_dump(),
        notes_count=notes_count,
        recent_notes=[note for note in recent_notes]
    )


@router.put("/{keyword_id}", response_model=KeywordResponse)
async def update_keyword(
    keyword_id: uuid.UUID,
    keyword_update: KeywordUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> KeywordResponse:
    """
    Update keyword by ID.
    
    Args:
        keyword_id: Keyword ID
        keyword_update: Keyword update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated keyword information
        
    Raises:
        HTTPException: If keyword not found or doesn't belong to user
    """
    result = await db.execute(
        select(Keyword).where(
            Keyword.id == keyword_id,
            Keyword.user_id == current_user.id
        )
    )
    keyword = result.scalar_one_or_none()
    
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )
    
    # Update fields
    update_data = keyword_update.model_dump(exclude_unset=True)
    
    # Check for duplicate name if updating name
    if "name" in update_data:
        new_name = update_data["name"].lower()
        existing_result = await db.execute(
            select(Keyword).where(
                Keyword.name == new_name,
                Keyword.user_id == current_user.id,
                Keyword.id != keyword_id
            )
        )
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Keyword name already exists"
            )
        keyword.name = new_name
    
    keyword.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(keyword)
    
    return KeywordResponse.model_validate(keyword)


@router.delete("/{keyword_id}", response_model=MessageResponse)
async def delete_keyword(
    keyword_id: uuid.UUID,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Delete keyword by ID.
    
    Args:
        keyword_id: Keyword ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If keyword not found or doesn't belong to user
    """
    result = await db.execute(
        select(Keyword).where(
            Keyword.id == keyword_id,
            Keyword.user_id == current_user.id
        )
    )
    keyword = result.scalar_one_or_none()
    
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )
    
    # Check if keyword is being used
    from app.models.note import note_keywords
    usage_result = await db.execute(
        select(func.count())
        .select_from(note_keywords)
        .where(note_keywords.c.keyword_id == keyword_id)
    )
    usage_count = usage_result.scalar()
    
    if usage_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete keyword that is used by {usage_count} notes. Remove it from notes first."
        )
    
    await db.delete(keyword)
    await db.commit()
    
    return MessageResponse(message="Keyword deleted successfully")


@router.post("/bulk", response_model=List[KeywordResponse])
async def create_keywords_bulk(
    keyword_names: List[str],
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[KeywordResponse]:
    """
    Create multiple keywords in bulk.
    
    Args:
        keyword_names: List of keyword names to create
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of created keywords (existing keywords are skipped)
    """
    created_keywords = []
    
    for name in keyword_names:
        normalized_name = name.strip().lower()
        if not normalized_name:
            continue
            
        # Check if keyword already exists
        existing_result = await db.execute(
            select(Keyword).where(
                Keyword.name == normalized_name,
                Keyword.user_id == current_user.id
            )
        )
        existing_keyword = existing_result.scalar_one_or_none()
        
        if not existing_keyword:
            # Create new keyword
            new_keyword = Keyword(
                name=normalized_name,
                user_id=current_user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(new_keyword)
            created_keywords.append(new_keyword)
    
    if created_keywords:
        await db.commit()
        for keyword in created_keywords:
            await db.refresh(keyword)
    
    return [KeywordResponse.model_validate(keyword) for keyword in created_keywords]