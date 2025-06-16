"""
Sources management endpoints
"""
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user
from app.models.source import Source
from app.models.note import Note
from app.schemas.user import UserInDB
from app.schemas.source import (
    SourceCreate, SourceUpdate, SourceResponse,
    SourceWithNotes, SourceDetail, WebSourceCreate, BookSourceCreate
)
from app.schemas.common import PaginatedResponse, MessageResponse


router = APIRouter()


@router.get("/", response_model=PaginatedResponse[SourceWithNotes])
async def list_sources(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    source_type: Optional[str] = Query(None),
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PaginatedResponse[SourceWithNotes]:
    """
    List user's sources with optional filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Search term for source name
        source_type: Filter by source type
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of sources
    """
    # Build query
    query = select(Source).where(Source.user_id == current_user.id)
    
    if search:
        query = query.where(Source.name.ilike(f"%{search}%"))
    
    if source_type:
        query = query.where(Source.source_type == source_type)
    
    # Get total count
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(Source.created_at.desc())
    result = await db.execute(query)
    sources = result.scalars().all()
    
    # Get notes count for each source
    sources_with_notes = []
    for source in sources:
        notes_count_query = select(func.count()).select_from(Note).where(Note.source_id == source.id)
        notes_count_result = await db.execute(notes_count_query)
        notes_count = notes_count_result.scalar()
        
        source_dict = SourceWithNotes.model_validate(source).model_dump()
        source_dict['notes_count'] = notes_count
        sources_with_notes.append(SourceWithNotes(**source_dict))
    
    return PaginatedResponse[SourceWithNotes](
        items=sources_with_notes,
        total=total,
        limit=limit,
        offset=skip,
        has_next=skip + limit < total,
        has_previous=skip > 0
    )


@router.get("/types", response_model=List[str])
async def get_source_types() -> List[str]:
    """
    Get available source types.
    
    Returns:
        List of available source types
    """
    return [
        "web", "book", "pdf", "video", "podcast", "article",
        "paper", "document", "image", "presentation", "other"
    ]


@router.post("/", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(
    source_data: SourceCreate,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SourceResponse:
    """
    Create a new source.
    
    Args:
        source_data: Source creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created source information
    """
    # Create new source
    new_source = Source(
        name=source_data.name,
        source_type=source_data.source_type,
        source_metadata=source_data.source_metadata,
        user_id=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_source)
    await db.commit()
    await db.refresh(new_source)
    
    return SourceResponse.model_validate(new_source)


@router.post("/web", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_web_source(
    source_data: WebSourceCreate,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SourceResponse:
    """
    Create a new web source with URL validation.
    
    Args:
        source_data: Web source creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created source information
    """
    # Create new web source
    new_source = Source(
        name=source_data.name,
        source_type="web",
        source_metadata=source_data.source_metadata,
        user_id=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_source)
    await db.commit()
    await db.refresh(new_source)
    
    return SourceResponse.model_validate(new_source)


@router.post("/book", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_book_source(
    source_data: BookSourceCreate,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SourceResponse:
    """
    Create a new book source with book-specific metadata.
    
    Args:
        source_data: Book source creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created source information
    """
    # Create new book source
    new_source = Source(
        name=source_data.name,
        source_type="book",
        source_metadata=source_data.source_metadata,
        user_id=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_source)
    await db.commit()
    await db.refresh(new_source)
    
    return SourceResponse.model_validate(new_source)


@router.get("/{source_id}", response_model=SourceDetail)
async def get_source(
    source_id: uuid.UUID,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SourceDetail:
    """
    Get source by ID with detailed information.
    
    Args:
        source_id: Source ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Detailed source information
        
    Raises:
        HTTPException: If source not found or doesn't belong to user
    """
    result = await db.execute(
        select(Source).where(
            Source.id == source_id,
            Source.user_id == current_user.id
        )
    )
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    # Get notes count and recent notes
    notes_count_query = select(func.count()).select_from(Note).where(Note.source_id == source_id)
    notes_count_result = await db.execute(notes_count_query)
    notes_count = notes_count_result.scalar()
    
    recent_notes_query = (
        select(Note)
        .where(
            Note.source_id == source_id,
            Note.user_id == current_user.id
        )
        .order_by(Note.updated_at.desc())
        .limit(5)
    )
    recent_notes_result = await db.execute(recent_notes_query)
    recent_notes = recent_notes_result.scalars().all()
    
    return SourceDetail(
        **SourceResponse.model_validate(source).model_dump(),
        notes_count=notes_count,
        recent_notes=[note for note in recent_notes]
    )


@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: uuid.UUID,
    source_update: SourceUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SourceResponse:
    """
    Update source by ID.
    
    Args:
        source_id: Source ID
        source_update: Source update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated source information
        
    Raises:
        HTTPException: If source not found or doesn't belong to user
    """
    result = await db.execute(
        select(Source).where(
            Source.id == source_id,
            Source.user_id == current_user.id
        )
    )
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    # Update fields
    update_data = source_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(source, field):
            setattr(source, field, value)
    
    source.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(source)
    
    return SourceResponse.model_validate(source)


@router.delete("/{source_id}", response_model=MessageResponse)
async def delete_source(
    source_id: uuid.UUID,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Delete source by ID.
    
    Args:
        source_id: Source ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If source not found or doesn't belong to user
    """
    result = await db.execute(
        select(Source).where(
            Source.id == source_id,
            Source.user_id == current_user.id
        )
    )
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    # Check if source has associated notes
    notes_count_result = await db.execute(
        select(func.count()).select_from(Note).where(Note.source_id == source_id)
    )
    notes_count = notes_count_result.scalar()
    
    if notes_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete source that has {notes_count} associated notes. Remove or reassign notes first."
        )
    
    await db.delete(source)
    await db.commit()
    
    return MessageResponse(message="Source deleted successfully")


@router.get("/{source_id}/notes", response_model=PaginatedResponse[dict])
async def get_source_notes(
    source_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PaginatedResponse[dict]:
    """
    Get notes associated with a specific source.
    
    Args:
        source_id: Source ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of notes for the source
        
    Raises:
        HTTPException: If source not found or doesn't belong to user
    """
    # Verify source exists and belongs to user
    source_result = await db.execute(
        select(Source).where(
            Source.id == source_id,
            Source.user_id == current_user.id
        )
    )
    source = source_result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    # Get notes for this source
    query = select(Note).where(
        Note.source_id == source_id,
        Note.user_id == current_user.id
    )
    
    # Get total count
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(Note.updated_at.desc())
    result = await db.execute(query)
    notes = result.scalars().all()
    
    return PaginatedResponse[dict](
        items=[{
            "id": str(note.id),
            "title": note.title,
            "content": note.content[:200] + "..." if len(note.content) > 200 else note.content,
            "note_type": note.note_type,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat()
        } for note in notes],
        total=total,
        limit=limit,
        offset=skip,
        has_next=skip + limit < total,
        has_previous=skip > 0
    )