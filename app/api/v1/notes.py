from datetime import date as date_type
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.utils import create_paginated_response, get_skip_limit
from app.db.session import get_db
from app.models.journal import Journal
from app.models.note import Note
from app.models.tag import Tag
from app.schemas.note import NoteCreate, NoteRead, NoteUpdate
from app.schemas.response import (
    DataResponse,
    ListResponse,
    MessageResponse,
    PaginatedResponse,
)
from app.schemas.tag import TagRead

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[NoteRead])
def list_notes(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    date: date_type | None = Query(
        None, description="Filter by creation date (YYYY-MM-DD)"
    ),
    journal_id: UUID | None = Query(None, description="Filter by journal ID"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a paginated list of notes.

    Optionally filter by creation date or journal_id using query parameters.
    """
    # Get pagination values
    skip, limit = get_skip_limit(page, per_page)

    # Build base query
    query = db.query(Note)

    # Apply filters if provided
    if date:
        # Filter for notes where the date part of created_at matches the provided date
        query = query.filter(func.date(Note.created_at) == date)
    if journal_id:
        query = query.filter(Note.journal_id == journal_id)

    # Get total count with filters applied
    total = query.count()

    # Query notes with pagination
    notes = query.offset(skip).limit(limit).all()

    # Build filter message
    filter_msg = ""
    if date or journal_id:
        filters = []
        if date:
            filters.append(f"date={date}")
        if journal_id:
            filters.append(f"journal_id={journal_id}")
        filter_msg = f" with filters: {', '.join(filters)}"

    # Return paginated response
    return create_paginated_response(
        data=notes,
        page=page,
        per_page=per_page,
        total=total,
        message=f"Notes retrieved successfully{filter_msg}",
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=DataResponse[NoteRead],
)
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new note.
    """
    # Validate journal exists if journal_id is provided
    if note.journal_id:
        journal = db.query(Journal).filter(Journal.id == note.journal_id).first()
        if not journal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Journal with id {note.journal_id} not found",
            )

    new_note = Note(
        text=note.text,
        meta=note.meta,
        journal_id=note.journal_id,
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return DataResponse[NoteRead](
        success=True,
        message="Note created successfully",
        data=new_note,
    )


@router.get("/{note_id}", response_model=DataResponse[NoteRead])
def get_note(
    note_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific note by ID.
    """
    note = db.query(Note).filter(Note.id == note_id).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

    return DataResponse[NoteRead](
        success=True,
        message="Note retrieved successfully",
        data=note,
    )


@router.put("/{note_id}", response_model=DataResponse[NoteRead])
def update_note(
    note_id: UUID,
    note: NoteUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a specific note by ID.
    """
    existing_note = db.query(Note).filter(Note.id == note_id).first()

    if not existing_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

    # Validate journal exists if journal_id is provided
    if note.journal_id:
        journal = db.query(Journal).filter(Journal.id == note.journal_id).first()
        if not journal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Journal with id {note.journal_id} not found",
            )

    # Update note fields (tags are managed via separate relationship endpoints)
    existing_note.text = note.text
    existing_note.meta = note.meta
    if note.journal_id is not None:
        existing_note.journal_id = note.journal_id

    db.commit()
    db.refresh(existing_note)

    return DataResponse[NoteRead](
        success=True,
        message="Note updated successfully",
        data=existing_note,
    )


@router.get("/{note_id}/tags", response_model=ListResponse[TagRead])
def get_note_tags(
    note_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get all tags for a specific note.
    """
    # Verify note exists
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

    # Get all tags for this note
    tags = note.tags

    return ListResponse[TagRead](
        success=True,
        message=f"Retrieved {len(tags)} tag(s) for note {note_id}",
        data=tags,
        count=len(tags),
    )


@router.post("/{note_id}/tags/{tag_id}", response_model=MessageResponse)
def add_tag_to_note(
    note_id: UUID,
    tag_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Add a tag to a note.
    """
    # Verify note exists
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

    # Verify tag exists
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found",
        )

    # Check if tag is already associated with note
    if tag in note.tags:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tag {tag_id} is already associated with note {note_id}",
        )

    # Add tag to note
    note.tags.append(tag)
    db.commit()

    return MessageResponse(
        success=True,
        message=f"Tag '{tag.name}' added to note {note_id}",
    )


@router.delete("/{note_id}/tags/{tag_id}", response_model=MessageResponse)
def remove_tag_from_note(
    note_id: UUID,
    tag_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Remove a tag from a note.
    """
    # Verify note exists
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

    # Verify tag exists
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found",
        )

    # Check if tag is associated with note
    if tag not in note.tags:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag {tag_id} is not associated with note {note_id}",
        )

    # Remove tag from note
    note.tags.remove(tag)
    db.commit()

    return MessageResponse(
        success=True,
        message=f"Tag '{tag.name}' removed from note {note_id}",
    )


@router.delete("/{note_id}", response_model=MessageResponse)
def delete_note(
    note_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete a specific note by ID.

    Note: Tag associations will be automatically removed.
    """
    existing_note = db.query(Note).filter(Note.id == note_id).first()

    if not existing_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

    # Count tags for informative message
    tag_count = len(existing_note.tags)

    db.delete(existing_note)
    db.commit()

    message = f"Note {note_id} deleted successfully"
    if tag_count > 0:
        message += f" ({tag_count} tag association(s) removed)"

    return MessageResponse(
        success=True,
        message=message,
    )
