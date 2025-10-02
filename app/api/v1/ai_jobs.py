from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.utils import create_paginated_response, get_skip_limit
from app.db.session import get_db
from app.models.ai import AIJob, AIJobStatus
from app.models.journal import Journal
from app.schemas.ai import AIJobCreate, AIJobRead, AIJobUpdate
from app.schemas.response import DataResponse, MessageResponse, PaginatedResponse

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[AIJobRead])
def list_ai_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: AIJobStatus | None = Query(
        None, alias="status", description="Filter by job status"
    ),
    journal_id: UUID | None = Query(None, description="Filter by journal ID"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a paginated list of AI jobs.

    Optionally filter by status or journal_id.
    """
    # Get pagination values
    skip, limit = get_skip_limit(page, per_page)

    # Build base query
    query = db.query(AIJob)

    # Apply filters
    if status_filter:
        query = query.filter(AIJob.status == status_filter)
    if journal_id:
        query = query.filter(AIJob.journal_id == journal_id)

    # Get total count with filters applied
    total = query.count()

    # Query AI jobs with pagination
    ai_jobs = query.offset(skip).limit(limit).all()

    # Return paginated response
    filter_msg = ""
    if status_filter or journal_id:
        filters = []
        if status_filter:
            filters.append(f"status={status_filter.value}")
        if journal_id:
            filters.append(f"journal_id={journal_id}")
        filter_msg = f" with filters: {', '.join(filters)}"

    return create_paginated_response(
        data=ai_jobs,
        page=page,
        per_page=per_page,
        total=total,
        message=f"AI jobs retrieved successfully{filter_msg}",
    )


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=DataResponse[AIJobRead],
)
def create_ai_job(
    ai_job: AIJobCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new AI job.
    """
    # Validate journal exists (required for AI jobs)
    journal = db.query(Journal).filter(Journal.id == ai_job.journal_id).first()
    if not journal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journal with id {ai_job.journal_id} not found",
        )

    new_ai_job = AIJob(
        journal_id=ai_job.journal_id,
        model_name=ai_job.model_name,
        model_version=ai_job.model_version,
        prompt=ai_job.prompt,
        status=AIJobStatus.QUEUED,  # Default status for new jobs
    )
    db.add(new_ai_job)
    db.commit()
    db.refresh(new_ai_job)
    return DataResponse[AIJobRead](
        success=True,
        message="AI job created successfully",
        data=new_ai_job,
    )


@router.get("/{ai_job_id}", response_model=DataResponse[AIJobRead])
def get_ai_job(
    ai_job_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific AI job by ID.
    """
    ai_job = db.query(AIJob).filter(AIJob.id == ai_job_id).first()

    if not ai_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI job with id {ai_job_id} not found",
        )

    return DataResponse[AIJobRead](
        success=True,
        message="AI job retrieved successfully",
        data=ai_job,
    )


@router.put("/{ai_job_id}", response_model=DataResponse[AIJobRead])
def update_ai_job(
    ai_job_id: UUID,
    ai_job: AIJobUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a specific AI job by ID.

    Typically used to update status, response, error_message, or meta fields.
    """
    existing_ai_job = db.query(AIJob).filter(AIJob.id == ai_job_id).first()

    if not existing_ai_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI job with id {ai_job_id} not found",
        )

    # Update only provided fields
    if ai_job.status is not None:
        existing_ai_job.status = ai_job.status
    if ai_job.response is not None:
        existing_ai_job.response = ai_job.response
    if ai_job.error_message is not None:
        existing_ai_job.error_message = ai_job.error_message
    if ai_job.meta is not None:
        existing_ai_job.meta = ai_job.meta

    db.commit()
    db.refresh(existing_ai_job)

    return DataResponse[AIJobRead](
        success=True,
        message="AI job updated successfully",
        data=existing_ai_job,
    )


@router.delete("/{ai_job_id}", response_model=MessageResponse)
def delete_ai_job(
    ai_job_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete a specific AI job by ID.
    """
    existing_ai_job = db.query(AIJob).filter(AIJob.id == ai_job_id).first()

    if not existing_ai_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI job with id {ai_job_id} not found",
        )

    db.delete(existing_ai_job)
    db.commit()

    return MessageResponse(
        success=True,
        message=f"AI job {ai_job_id} deleted successfully",
    )
