from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.utils import create_paginated_response, get_skip_limit
from app.db.session import get_db
from app.models.tag import Tag
from app.schemas.note import NoteRead
from app.schemas.response import (
    DataResponse,
    ListResponse,
    MessageResponse,
    PaginatedResponse,
)
from app.schemas.tag import TagCreate, TagRead, TagUpdate

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[TagRead])
def list_tags(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a paginated list of tags.
    """
    # Get pagination values
    skip, limit = get_skip_limit(page, per_page)

    # Build base query
    query = db.query(Tag)

    # Get total count
    total = query.count()

    # Query tags with pagination
    tags = query.offset(skip).limit(limit).all()

    # Return paginated response
    return create_paginated_response(
        data=tags,
        page=page,
        per_page=per_page,
        total=total,
        message="Tags retrieved successfully",
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=DataResponse[TagRead],
)
def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new tag.
    """
    # Check if tag with same name already exists
    existing_tag = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tag with name '{tag.name}' already exists",
        )

    new_tag = Tag(name=tag.name)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return DataResponse[TagRead](
        success=True,
        message="Tag created successfully",
        data=new_tag,
    )


@router.get("/{tag_id}", response_model=DataResponse[TagRead])
def get_tag(
    tag_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific tag by ID.
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found",
        )

    return DataResponse[TagRead](
        success=True,
        message="Tag retrieved successfully",
        data=tag,
    )


@router.put("/{tag_id}", response_model=DataResponse[TagRead])
def update_tag(
    tag_id: UUID,
    tag: TagUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a specific tag by ID.
    """
    existing_tag = db.query(Tag).filter(Tag.id == tag_id).first()

    if not existing_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found",
        )

    # Check if another tag with the same name exists (excluding current)
    name_conflict = db.query(Tag).filter(Tag.name == tag.name, Tag.id != tag_id).first()
    if name_conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tag with name '{tag.name}' already exists",
        )

    existing_tag.name = tag.name

    db.commit()
    db.refresh(existing_tag)

    return DataResponse[TagRead](
        success=True,
        message="Tag updated successfully",
        data=existing_tag,
    )


@router.get("/{tag_id}/notes", response_model=ListResponse[NoteRead])
def get_tag_notes(
    tag_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get all notes associated with a specific tag.
    """
    # Verify tag exists
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found",
        )

    # Get all notes for this tag
    notes = tag.notes

    return ListResponse[NoteRead](
        success=True,
        message=f"Retrieved {len(notes)} note(s) for tag '{tag.name}'",
        data=notes,
        count=len(notes),
    )


@router.delete("/{tag_id}", response_model=MessageResponse)
def delete_tag(
    tag_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete a specific tag by ID.

    Note: This will remove the tag from all associated notes.
    """
    existing_tag = db.query(Tag).filter(Tag.id == tag_id).first()

    if not existing_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found",
        )

    # Count notes for informative message
    note_count = len(existing_tag.notes)

    db.delete(existing_tag)
    db.commit()

    message = f"Tag '{existing_tag.name}' deleted successfully"
    if note_count > 0:
        message += f" (removed from {note_count} note(s))"

    return MessageResponse(
        success=True,
        message=message,
    )
