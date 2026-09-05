"""
Job application CRUD routes. Every route is protected and every
single-object operation verifies the application belongs to the
currently logged-in user (ownership enforcement / access control).
"""
from typing import List, Optional
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import JobApplication, User, ApplicationStatus
from app.schemas import (
    JobApplicationCreate, 
    JobApplicationUpdate, 
    JobApplicationOut,
    PaginatedApplicationsResponse
)
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/applications", tags=["Job Applications"])


def _get_owned_application_or_404(
    application_id: int, db: Session, current_user: User
) -> JobApplication:
    """
    Fetch an application by id, scoped to the current user.
    Returns 404 (not 403) for applications that exist but belong to someone
    else, so we don't leak whether the id exists at all.
    """
    application = (
        db.query(JobApplication)
        .filter(
            JobApplication.id == application_id,
            JobApplication.user_id == current_user.id,
        )
        .first()
    )
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    return application


@router.post("/", response_model=JobApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(
    application_in: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new job application for the logged-in user."""
    new_application = JobApplication(
        user_id=current_user.id,
        **application_in.model_dump(),
    )
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    
    logger.info(
        f"Application created: {new_application.company} - {new_application.role} "
        f"(ID: {new_application.id}, User: {current_user.id})"
    )
    return new_application


@router.get("/", response_model=PaginatedApplicationsResponse)
def list_applications(
    status_filter: Optional[ApplicationStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    page_size: int = Query(
        settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description=f"Items per page (max {settings.MAX_PAGE_SIZE})"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List applications belonging to the logged-in user with pagination.
    
    Returns:
    - items: List of applications for current page
    - total: Total count of applications matching filters
    - page: Current page number
    - page_size: Items per page
    - total_pages: Total number of pages
    """
    query = db.query(JobApplication).filter(JobApplication.user_id == current_user.id)
    
    if status_filter is not None:
        query = query.filter(JobApplication.status == status_filter)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    applications = query.order_by(
        JobApplication.created_at.desc()
    ).offset(offset).limit(page_size).all()
    
    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size  # Ceiling division
    
    logger.info(
        f"Applications listed: {len(applications)} items "
        f"(page {page}/{total_pages}, user: {current_user.id})"
    )
    
    return PaginatedApplicationsResponse(
        items=applications,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )


@router.get("/{application_id}", response_model=JobApplicationOut)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single application by id (must belong to the current user)."""
    return _get_owned_application_or_404(application_id, db, current_user)


@router.put("/{application_id}", response_model=JobApplicationOut)
def update_application(
    application_id: int,
    application_update: JobApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update one or more fields of an existing application."""
    application = _get_owned_application_or_404(application_id, db, current_user)

    update_data = application_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(application, field, value)

    db.commit()
    db.refresh(application)
    
    logger.info(
        f"Application updated: ID {application_id} "
        f"(fields: {list(update_data.keys())}, user: {current_user.id})"
    )
    return application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an application owned by the current user."""
    application = _get_owned_application_or_404(application_id, db, current_user)
    
    logger.info(
        f"Application deleted: {application.company} - {application.role} "
        f"(ID: {application_id}, user: {current_user.id})"
    )
    
    db.delete(application)
    db.commit()
    return None
