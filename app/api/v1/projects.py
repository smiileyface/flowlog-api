from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.utils import create_paginated_response, get_skip_limit
from app.db.session import get_db
from app.models.journal import Journal
from app.models.project import Project
from app.schemas.journal import JournalRead
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.schemas.response import (
    DataResponse,
    ListResponse,
    MessageResponse,
    PaginatedResponse,
)

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[ProjectRead])
def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a paginated list of projects.
    """
    # Get pagination values
    skip, limit = get_skip_limit(page, per_page)

    # Build base query
    query = db.query(Project)

    # Get total count
    total = query.count()

    # Query projects with pagination
    projects = query.offset(skip).limit(limit).all()

    # Return paginated response
    return create_paginated_response(
        data=projects,
        page=page,
        per_page=per_page,
        total=total,
        message="Projects retrieved successfully",
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=DataResponse[ProjectRead],
)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new project.
    """
    # Check if project with same name already exists
    existing_project = db.query(Project).filter(Project.name == project.name).first()
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project with name '{project.name}' already exists",
        )

    new_project = Project(name=project.name, description=project.description)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return DataResponse[ProjectRead](
        success=True,
        message="Project created successfully",
        data=new_project,
    )


@router.get("/{project_id}", response_model=DataResponse[ProjectRead])
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific project by ID.
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    return DataResponse[ProjectRead](
        success=True,
        message="Project retrieved successfully",
        data=project,
    )


@router.put("/{project_id}", response_model=DataResponse[ProjectRead])
def update_project(
    project_id: UUID,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a specific project by ID.
    """
    existing_project = db.query(Project).filter(Project.id == project_id).first()

    if not existing_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Check if another project with the same name exists (excluding current)
    name_conflict = (
        db.query(Project)
        .filter(Project.name == project.name, Project.id != project_id)
        .first()
    )
    if name_conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project with name '{project.name}' already exists",
        )

    existing_project.name = project.name
    existing_project.description = project.description

    db.commit()
    db.refresh(existing_project)

    return DataResponse[ProjectRead](
        success=True,
        message="Project updated successfully",
        data=existing_project,
    )


@router.get("/{project_id}/journals", response_model=ListResponse[JournalRead])
def get_project_journals(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get all journals for a specific project.
    """
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Get all journals for this project
    journals = db.query(Journal).filter(Journal.project_id == project_id).all()

    return ListResponse[JournalRead](
        success=True,
        message=f"Retrieved {len(journals)} journal(s) for project {project_id}",
        data=journals,  # type: ignore[arg-type]
        count=len(journals),
    )


@router.delete("/{project_id}", response_model=MessageResponse)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete a specific project by ID.

    WARNING: This will cascade delete all associated journals and their related data.
    """
    existing_project = db.query(Project).filter(Project.id == project_id).first()

    if not existing_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Count related journals for informative message
    journal_count = db.query(Journal).filter(Journal.project_id == project_id).count()

    db.delete(existing_project)
    db.commit()

    message = f"Project {project_id} deleted successfully"
    if journal_count > 0:
        message += f" (cascade deleted {journal_count} journal(s))"

    return MessageResponse(
        success=True,
        message=message,
    )
