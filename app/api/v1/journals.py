from datetime import date as date_type
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.utils import create_paginated_response, get_skip_limit
from app.db.session import get_db
from app.models.ai import AIJob
from app.models.journal import Journal
from app.models.note import Note
from app.models.project import Project
from app.schemas.ai import AIJobRead
from app.schemas.journal import JournalCreate, JournalRead, JournalUpdate
from app.schemas.note import NoteRead
from app.schemas.response import (
    DataResponse,
    ListResponse,
    MessageResponse,
    PaginatedResponse,
)

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[JournalRead])
def list_journals(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    date: date_type | None = Query(
        None, description="Filter by creation date (YYYY-MM-DD)"
    ),
    project_id: UUID | None = Query(None, description="Filter by project ID"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a paginated list of journals.

    Optionally filter by creation date or project_id using query parameters.
    """
    # Get pagination values
    skip, limit = get_skip_limit(page, per_page)

    # Build base query
    query = db.query(Journal)

    # Apply filters if provided
    if date:
        # Filter for journals where the date part of the date matches the provided date
        query = query.filter(func.date(Journal.date) == date)
    if project_id:
        query = query.filter(Journal.project_id == project_id)

    # Get total count with filters applied
    total = query.count()

    # Query journals with pagination
    journals = query.offset(skip).limit(limit).all()

    # Build filter message
    filter_msg = ""
    if date or project_id:
        filters = []
        if date:
            filters.append(f"date={date}")
        if project_id:
            filters.append(f"project_id={project_id}")
        filter_msg = f" with filters: {', '.join(filters)}"

    # Return paginated response
    return create_paginated_response(
        data=journals,
        page=page,
        per_page=per_page,
        total=total,
        message=f"Journals retrieved successfully{filter_msg}",
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=DataResponse[JournalRead],
)
def create_journal(
    journal: JournalCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new journal.
    """
    # Validate project exists if project_id is provided
    if journal.project_id:
        project = db.query(Project).filter(Project.id == journal.project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {journal.project_id} not found",
            )

    new_journal = Journal(date=journal.date, project_id=journal.project_id)
    db.add(new_journal)
    db.commit()
    db.refresh(new_journal)
    return DataResponse[JournalRead](
        success=True,
        message="Journal created successfully",
        data=new_journal,
    )


@router.get("/{journal_id}", response_model=DataResponse[JournalRead])
def get_journal(
    journal_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific journal by ID.
    """
    journal = db.query(Journal).filter(Journal.id == journal_id).first()

    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journal with id {journal_id} not found",
        )

    return DataResponse[JournalRead](
        success=True,
        message="Journal retrieved successfully",
        data=journal,
    )


@router.put("/{journal_id}", response_model=DataResponse[JournalRead])
def update_journal(
    journal_id: UUID,
    journal: JournalUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a specific journal by ID.
    """
    existing_journal = db.query(Journal).filter(Journal.id == journal_id).first()

    if not existing_journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journal with id {journal_id} not found",
        )

    # Validate project exists if project_id is provided
    if journal.project_id:
        project = db.query(Project).filter(Project.id == journal.project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {journal.project_id} not found",
            )

    existing_journal.date = journal.date
    existing_journal.processed_markdown = journal.processed_markdown
    existing_journal.notes_snapshot = journal.notes_snapshot
    existing_journal.project_id = journal.project_id

    db.commit()
    db.refresh(existing_journal)

    return DataResponse[JournalRead](
        success=True,
        message="Journal updated successfully",
        data=existing_journal,
    )


@router.get("/{journal_id}/notes", response_model=ListResponse[NoteRead])
def get_journal_notes(
    journal_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get all notes for a specific journal.
    """
    # Verify journal exists
    journal = db.query(Journal).filter(Journal.id == journal_id).first()
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journal with id {journal_id} not found",
        )

    # Get all notes for this journal
    notes = db.query(Note).filter(Note.journal_id == journal_id).all()

    return ListResponse[NoteRead](
        success=True,
        message=f"Retrieved {len(notes)} note(s) for journal {journal_id}",
        data=notes,  # type: ignore[arg-type]
        count=len(notes),
    )


@router.get("/{journal_id}/ai-jobs", response_model=ListResponse[AIJobRead])
def get_journal_ai_jobs(
    journal_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get all AI jobs for a specific journal.
    """
    # Verify journal exists
    journal = db.query(Journal).filter(Journal.id == journal_id).first()
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journal with id {journal_id} not found",
        )

    # Get all AI jobs for this journal
    ai_jobs = db.query(AIJob).filter(AIJob.journal_id == journal_id).all()

    return ListResponse[AIJobRead](
        success=True,
        message=f"Retrieved {len(ai_jobs)} AI job(s) for journal {journal_id}",
        data=ai_jobs,  # type: ignore[arg-type]
        count=len(ai_jobs),
    )


@router.delete("/{journal_id}", response_model=MessageResponse)
def delete_journal(
    journal_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete a specific journal by ID.

    Note: Related notes and AI jobs may be affected depending on cascade settings.
    """
    existing_journal = db.query(Journal).filter(Journal.id == journal_id).first()

    if not existing_journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journal with id {journal_id} not found",
        )

    # Count related resources for informative message
    note_count = db.query(Note).filter(Note.journal_id == journal_id).count()
    ai_job_count = db.query(AIJob).filter(AIJob.journal_id == journal_id).count()

    db.delete(existing_journal)
    db.commit()

    message = f"Journal {journal_id} deleted successfully"
    related_info = []
    if note_count > 0:
        related_info.append(f"{note_count} note(s) orphaned")
    if ai_job_count > 0:
        related_info.append(f"{ai_job_count} AI job(s) affected")
    if related_info:
        message += f" ({', '.join(related_info)})"

    return MessageResponse(
        success=True,
        message=message,
    )
