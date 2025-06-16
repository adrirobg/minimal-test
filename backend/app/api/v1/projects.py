"""
Project management endpoints
"""
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_user
from app.models.project import Project
from app.models.note import Note
from app.schemas.user import UserInDB
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, 
    ProjectWithNotes, ProjectTree
)
from app.schemas.common import PaginatedResponse, MessageResponse


router = APIRouter()


@router.get("/", response_model=PaginatedResponse[ProjectWithNotes])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    parent_id: Optional[uuid.UUID] = Query(None),
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PaginatedResponse[ProjectWithNotes]:
    """
    List user's projects with optional filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Search term for project name or description
        parent_id: Filter by parent project ID (None for root projects)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of projects
    """
    # Build query
    query = select(Project).where(Project.user_id == current_user.id)
    
    if search:
        search_filter = (
            Project.name.ilike(f"%{search}%") |
            Project.description.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    if parent_id is not None:
        query = query.where(Project.parent_project_id == parent_id)
    else:
        # If parent_id is None, show only root projects
        query = query.where(Project.parent_project_id.is_(None))
    
    # Get total count
    total_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(Project.created_at.desc())
    result = await db.execute(query)
    projects = result.scalars().all()
    
    # Get notes count for each project
    projects_with_notes = []
    for project in projects:
        notes_count_query = select(func.count()).select_from(Note).where(Note.project_id == project.id)
        notes_count_result = await db.execute(notes_count_query)
        notes_count = notes_count_result.scalar()
        
        project_dict = ProjectWithNotes.model_validate(project).model_dump()
        project_dict['notes_count'] = notes_count
        projects_with_notes.append(ProjectWithNotes(**project_dict))
    
    return PaginatedResponse[ProjectWithNotes](
        items=projects_with_notes,
        total=total,
        limit=limit,
        offset=skip,
        has_next=skip + limit < total,
        has_previous=skip > 0
    )


@router.get("/tree", response_model=List[ProjectTree])
async def get_project_tree(
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[ProjectTree]:
    """
    Get hierarchical project tree for current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Hierarchical project tree
    """
    # Get all user projects
    result = await db.execute(
        select(Project)
        .where(Project.user_id == current_user.id)
        .order_by(Project.name)
    )
    all_projects = result.scalars().all()
    
    # Build project tree
    projects_dict = {}
    root_projects = []
    
    # First pass: create all project objects
    for project in all_projects:
        # Get notes count
        notes_count_query = select(func.count()).select_from(Note).where(Note.project_id == project.id)
        notes_count_result = await db.execute(notes_count_query)
        notes_count = notes_count_result.scalar()
        
        project_tree = ProjectTree(
            **ProjectResponse.model_validate(project).model_dump(),
            children=[],
            notes_count=notes_count,
            total_notes_count=notes_count  # Will be calculated later
        )
        projects_dict[project.id] = project_tree
        
        if project.parent_project_id is None:
            root_projects.append(project_tree)
    
    # Second pass: build hierarchy
    for project in all_projects:
        if project.parent_project_id and project.parent_project_id in projects_dict:
            parent = projects_dict[project.parent_project_id]
            child = projects_dict[project.id]
            parent.children.append(child)
    
    # Third pass: calculate total notes count (including children)
    def calculate_total_notes(project_tree: ProjectTree) -> int:
        total = project_tree.notes_count
        for child in project_tree.children:
            total += calculate_total_notes(child)
        project_tree.total_notes_count = total
        return total
    
    for root_project in root_projects:
        calculate_total_notes(root_project)
    
    return root_projects


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """
    Create a new project.
    
    Args:
        project_data: Project creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created project information
        
    Raises:
        HTTPException: If parent project doesn't exist or doesn't belong to user
    """
    # Validate parent project if specified
    if project_data.parent_project_id:
        parent_result = await db.execute(
            select(Project).where(
                Project.id == project_data.parent_project_id,
                Project.user_id == current_user.id
            )
        )
        parent_project = parent_result.scalar_one_or_none()
        
        if not parent_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent project not found"
            )
    
    # Create new project
    new_project = Project(
        name=project_data.name,
        description=project_data.description,
        parent_project_id=project_data.parent_project_id,
        user_id=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    
    return ProjectResponse.model_validate(new_project)


@router.get("/{project_id}", response_model=ProjectWithNotes)
async def get_project(
    project_id: uuid.UUID,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ProjectWithNotes:
    """
    Get project by ID.
    
    Args:
        project_id: Project ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Project information with notes count
        
    Raises:
        HTTPException: If project not found or doesn't belong to user
    """
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get notes count
    notes_count_query = select(func.count()).select_from(Note).where(Note.project_id == project.id)
    notes_count_result = await db.execute(notes_count_query)
    notes_count = notes_count_result.scalar()
    
    project_dict = ProjectWithNotes.model_validate(project).model_dump()
    project_dict['notes_count'] = notes_count
    
    return ProjectWithNotes(**project_dict)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    project_update: ProjectUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """
    Update project by ID.
    
    Args:
        project_id: Project ID
        project_update: Project update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated project information
        
    Raises:
        HTTPException: If project not found or doesn't belong to user
    """
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Validate parent project if changing
    update_data = project_update.model_dump(exclude_unset=True)
    if "parent_project_id" in update_data and update_data["parent_project_id"]:
        # Check if new parent exists and belongs to user
        parent_result = await db.execute(
            select(Project).where(
                Project.id == update_data["parent_project_id"],
                Project.user_id == current_user.id
            )
        )
        parent_project = parent_result.scalar_one_or_none()
        
        if not parent_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent project not found"
            )
        
        # Check for circular reference
        if update_data["parent_project_id"] == project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project cannot be its own parent"
            )
    
    # Update fields
    for field, value in update_data.items():
        if hasattr(project, field):
            setattr(project, field, value)
    
    project.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(project)
    
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", response_model=MessageResponse)
async def delete_project(
    project_id: uuid.UUID,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Delete project by ID.
    
    Args:
        project_id: Project ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If project not found or doesn't belong to user
    """
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if project has children
    children_result = await db.execute(
        select(func.count()).select_from(Project).where(Project.parent_project_id == project_id)
    )
    children_count = children_result.scalar()
    
    if children_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete project with child projects. Delete or move child projects first."
        )
    
    # Delete project (cascade will handle related notes)
    await db.delete(project)
    await db.commit()
    
    return MessageResponse(message="Project deleted successfully")