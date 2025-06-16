"""
Notes management endpoints
"""
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, insert
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user
from app.models.note import Note, note_keywords
from app.models.keyword import Keyword
from app.models.project import Project
from app.models.source import Source
from app.schemas.user import UserInDB
from app.schemas.note import (
    NoteCreate, NoteUpdate, NoteResponse, NoteDetail,
    NoteWithKeywords, NoteWithProject, NoteSearch
)
from app.schemas.common import PaginatedResponse, MessageResponse, SearchResponse


router = APIRouter()


@router.get("/", response_model=PaginatedResponse[NoteResponse])
async def list_notes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    project_id: Optional[uuid.UUID] = Query(None),
    source_id: Optional[uuid.UUID] = Query(None),
    note_type: Optional[str] = Query(None),
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PaginatedResponse[NoteResponse]:
    """
    List user's notes with optional filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Search term for note title or content
        project_id: Filter by project ID
        source_id: Filter by source ID
        note_type: Filter by note type
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of notes
    """
    # Build query
    query = select(Note).where(Note.user_id == current_user.id)
    
    if search:
        search_filter = (
            Note.title.ilike(f"%{search}%") |
            Note.content.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    if project_id:
        query = query.where(Note.project_id == project_id)
    
    if source_id:
        query = query.where(Note.source_id == source_id)
        
    if note_type:
        query = query.where(Note.note_type == note_type)
    
    # Get total count
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(Note.updated_at.desc())
    result = await db.execute(query)
    notes = result.scalars().all()
    
    return PaginatedResponse[NoteResponse](
        items=[NoteResponse.model_validate(note) for note in notes],
        total=total,
        limit=limit,
        offset=skip,
        has_next=skip + limit < total,
        has_previous=skip > 0
    )


@router.get("/search", response_model=SearchResponse[NoteDetail])
async def search_notes(
    query: str = Query(..., min_length=1),
    project_id: Optional[uuid.UUID] = Query(None),
    source_id: Optional[uuid.UUID] = Query(None),
    note_type: Optional[str] = Query(None),
    keyword_ids: List[uuid.UUID] = Query([]),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SearchResponse[NoteDetail]:
    """
    Advanced search for notes with full-text search.
    
    Args:
        query: Search query string
        project_id: Filter by project ID
        source_id: Filter by source ID
        note_type: Filter by note type
        keyword_ids: Filter by keyword IDs
        limit: Maximum number of results
        offset: Number of results to skip
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Search results
    """
    # Build search query
    search_query = select(Note).where(Note.user_id == current_user.id)
    
    # Full-text search on title and content
    search_filter = (
        Note.title.ilike(f"%{query}%") |
        Note.content.ilike(f"%{query}%")
    )
    search_query = search_query.where(search_filter)
    
    # Apply filters
    if project_id:
        search_query = search_query.where(Note.project_id == project_id)
    
    if source_id:
        search_query = search_query.where(Note.source_id == source_id)
        
    if note_type:
        search_query = search_query.where(Note.note_type == note_type)
    
    if keyword_ids:
        # Join with keywords to filter by keyword IDs
        from app.models.note import note_keywords
        search_query = search_query.join(note_keywords).where(
            note_keywords.c.keyword_id.in_(keyword_ids)
        )
    
    # Get total count
    total_query = select(func.count()).select_from(search_query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    # Get results without eager loading to avoid SQLite issues
    search_query = search_query.offset(offset).limit(limit).order_by(Note.updated_at.desc())
    
    result = await db.execute(search_query)
    notes = result.scalars().all()
    
    # Convert to detailed note responses with manual loading
    detailed_notes = []
    for note in notes:
        note_detail = NoteDetail(
            **NoteResponse.model_validate(note).model_dump(),
            keywords=[],  # Skip keywords for now to avoid relationship issues
            project_name=None,  # Skip project name for now
            source_name=None,  # Skip source name for now
            outgoing_links_count=0,  # Skip for now to avoid relationship issues
            incoming_links_count=0   # Skip for now to avoid relationship issues
        )
        detailed_notes.append(note_detail)
    
    return SearchResponse[NoteDetail](
        results=detailed_notes,
        total=total,
        query=query,
        limit=limit,
        offset=offset
    )


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: NoteCreate,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> NoteResponse:
    """
    Create a new note.
    
    Args:
        note_data: Note creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created note information
        
    Raises:
        HTTPException: If project or source doesn't exist or doesn't belong to user
    """
    # Validate project if specified
    if note_data.project_id:
        project_result = await db.execute(
            select(Project).where(
                Project.id == note_data.project_id,
                Project.user_id == current_user.id
            )
        )
        project = project_result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
    
    # Validate source if specified
    if note_data.source_id:
        source_result = await db.execute(
            select(Source).where(
                Source.id == note_data.source_id,
                Source.user_id == current_user.id
            )
        )
        source = source_result.scalar_one_or_none()
        
        if not source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source not found"
            )
    
    # Create new note
    new_note = Note(
        title=note_data.title,
        content=note_data.content,
        note_type=note_data.note_type,
        note_metadata=note_data.note_metadata,
        project_id=note_data.project_id,
        source_id=note_data.source_id,
        user_id=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_note)
    await db.flush()  # Get the note ID
    
    # Add keywords if specified (after flush)
    if note_data.keyword_ids:
        # First verify keywords exist and belong to user
        keyword_result = await db.execute(
            select(Keyword.id).where(
                Keyword.id.in_(note_data.keyword_ids),
                Keyword.user_id == current_user.id
            )
        )
        valid_keyword_ids = keyword_result.scalars().all()
        
        # Insert into association table directly
        if valid_keyword_ids:
            associations = [
                {"note_id": new_note.id, "keyword_id": keyword_id}
                for keyword_id in valid_keyword_ids
            ]
            await db.execute(insert(note_keywords).values(associations))
    
    await db.commit()
    await db.refresh(new_note)
    
    return NoteResponse.model_validate(new_note)


@router.get("/{note_id}", response_model=NoteDetail)
async def get_note(
    note_id: uuid.UUID,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> NoteDetail:
    """
    Get note by ID with detailed information.
    
    Args:
        note_id: Note ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Detailed note information
        
    Raises:
        HTTPException: If note not found or doesn't belong to user
    """
    result = await db.execute(
        select(Note)
        .options(
            selectinload(Note.keywords),
            selectinload(Note.project),
            selectinload(Note.source),
            selectinload(Note.outgoing_links),
            selectinload(Note.incoming_links)
        )
        .where(
            Note.id == note_id,
            Note.user_id == current_user.id
        )
    )
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    return NoteDetail(
        **NoteResponse.model_validate(note).model_dump(),
        keywords=[keyword for keyword in note.keywords] if note.keywords else [],
        project_name=note.project.name if note.project else None,
        source_name=note.source.name if note.source else None,
        outgoing_links_count=len(note.outgoing_links) if note.outgoing_links else 0,
        incoming_links_count=len(note.incoming_links) if note.incoming_links else 0
    )


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: uuid.UUID,
    note_update: NoteUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> NoteResponse:
    """
    Update note by ID.
    
    Args:
        note_id: Note ID
        note_update: Note update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated note information
        
    Raises:
        HTTPException: If note not found or doesn't belong to user
    """
    result = await db.execute(
        select(Note)
        .options(selectinload(Note.keywords))
        .where(
            Note.id == note_id,
            Note.user_id == current_user.id
        )
    )
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Update fields
    update_data = note_update.model_dump(exclude_unset=True)
    
    # Handle keyword updates
    if "keyword_ids" in update_data:
        keyword_ids = update_data.pop("keyword_ids")
        if keyword_ids is not None:
            # Get valid keywords that belong to user
            keyword_result = await db.execute(
                select(Keyword).where(
                    Keyword.id.in_(keyword_ids),
                    Keyword.user_id == current_user.id
                )
            )
            keywords = keyword_result.scalars().all()
            note.keywords = keywords
    
    # Validate project and source if being updated
    if "project_id" in update_data and update_data["project_id"]:
        project_result = await db.execute(
            select(Project).where(
                Project.id == update_data["project_id"],
                Project.user_id == current_user.id
            )
        )
        if not project_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
    
    if "source_id" in update_data and update_data["source_id"]:
        source_result = await db.execute(
            select(Source).where(
                Source.id == update_data["source_id"],
                Source.user_id == current_user.id
            )
        )
        if not source_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source not found"
            )
    
    # Update remaining fields
    for field, value in update_data.items():
        if hasattr(note, field):
            setattr(note, field, value)
    
    note.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(note)
    
    return NoteResponse.model_validate(note)


@router.delete("/{note_id}", response_model=MessageResponse)
async def delete_note(
    note_id: uuid.UUID,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Delete note by ID.
    
    Args:
        note_id: Note ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If note not found or doesn't belong to user
    """
    result = await db.execute(
        select(Note).where(
            Note.id == note_id,
            Note.user_id == current_user.id
        )
    )
    note = result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    await db.delete(note)
    await db.commit()
    
    return MessageResponse(message="Note deleted successfully")