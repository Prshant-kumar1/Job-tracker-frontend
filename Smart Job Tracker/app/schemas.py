"""
Pydantic schemas used for request validation and response serialization.
"""
from datetime import date, datetime
from typing import Optional, List
import re

from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator, HttpUrl

from app.models import ApplicationStatus


# ---------------------------------------------------------------------------
# User / Auth schemas
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Sanitize name to prevent injection attacks."""
        # Remove leading/trailing whitespace
        v = v.strip()
        # Ensure it's not empty after stripping
        if not v:
            raise ValueError("Name cannot be empty or only whitespace")
        # Check for reasonable characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-'\.]+$", v):
            raise ValueError("Name contains invalid characters")
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Ensure password meets minimum security requirements."""
        if len(v) < 12:
            raise ValueError("Password must be at least 12 characters long")
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'\d', v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    token_type: Optional[str] = "access"  # "access" or "refresh"


# ---------------------------------------------------------------------------
# Job Application schemas
# ---------------------------------------------------------------------------

class JobApplicationCreate(BaseModel):
    company: str = Field(..., min_length=1, max_length=150)
    role: str = Field(..., min_length=1, max_length=150)
    location: Optional[str] = Field(None, max_length=150)
    apply_link: Optional[str] = Field(None, max_length=500)
    date_applied: Optional[date] = None
    status: ApplicationStatus = ApplicationStatus.APPLIED
    resume_version: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=5000)  # Limit notes to 5000 chars
    follow_up_date: Optional[date] = None
    
    @field_validator('company', 'role')
    @classmethod
    def validate_required_text(cls, v: str, info) -> str:
        """Sanitize required text fields."""
        v = v.strip()
        if not v:
            raise ValueError(f"{info.field_name} cannot be empty or only whitespace")
        return v
    
    @field_validator('apply_link')
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL format if provided."""
        if v is None or v.strip() == "":
            return None
        v = v.strip()
        # Basic URL validation
        if not re.match(r'^https?://', v, re.IGNORECASE):
            raise ValueError("URL must start with http:// or https://")
        # Check for reasonable URL length and characters
        if len(v) > 500:
            raise ValueError("URL is too long (max 500 characters)")
        return v
    
    @field_validator('date_applied', 'follow_up_date')
    @classmethod
    def validate_dates(cls, v: Optional[date], info) -> Optional[date]:
        """Validate dates are reasonable."""
        if v is None:
            return None
        # Date applied shouldn't be too far in the future
        if info.field_name == 'date_applied':
            if v > date.today():
                # Allow up to 7 days in the future for timezone differences
                days_ahead = (v - date.today()).days
                if days_ahead > 7:
                    raise ValueError("Application date cannot be more than 7 days in the future")
        # Follow-up date shouldn't be in the past
        if info.field_name == 'follow_up_date':
            if v < date.today():
                raise ValueError("Follow-up date should be in the future")
        return v
    
    @field_validator('notes', 'location', 'resume_version')
    @classmethod
    def sanitize_optional_text(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize optional text fields."""
        if v is None:
            return None
        v = v.strip()
        return v if v else None


class JobApplicationUpdate(BaseModel):
    """All fields optional — only provided fields are updated (PATCH-style PUT)."""

    company: Optional[str] = Field(None, min_length=1, max_length=150)
    role: Optional[str] = Field(None, min_length=1, max_length=150)
    location: Optional[str] = Field(None, max_length=150)
    apply_link: Optional[str] = Field(None, max_length=500)
    date_applied: Optional[date] = None
    status: Optional[ApplicationStatus] = None
    resume_version: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=5000)
    follow_up_date: Optional[date] = None
    
    # Apply same validators as Create
    @field_validator('company', 'role')
    @classmethod
    def validate_required_text(cls, v, info):
        if v is None:
            return v
        return JobApplicationCreate.validate_required_text.__func__(cls, v, info)
    _validate_url = field_validator('apply_link')(JobApplicationCreate.validate_url.__func__)
    _validate_dates = field_validator('date_applied', 'follow_up_date')(JobApplicationCreate.validate_dates.__func__)
    _sanitize_text = field_validator('notes', 'location', 'resume_version')(JobApplicationCreate.sanitize_optional_text.__func__)


class JobApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    company: str
    role: str
    location: Optional[str] = None
    apply_link: Optional[str] = None
    date_applied: Optional[date] = None
    status: ApplicationStatus
    resume_version: Optional[str] = None
    notes: Optional[str] = None
    follow_up_date: Optional[date] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Dashboard schemas
# ---------------------------------------------------------------------------

class PaginatedApplicationsResponse(BaseModel):
    """Response model for paginated applications list."""
    items: List[JobApplicationOut]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class DashboardSummaryResponse(BaseModel):
    total_applications: int
    applied_count: int
    oa_count: int
    interview_count: int
    rejected_count: int
    offer_count: int
    recent_applications: List[JobApplicationOut]
    upcoming_followups: List[JobApplicationOut]


# ---------------------------------------------------------------------------
# AI Suggestion schema
# ---------------------------------------------------------------------------

class AISuggestionResponse(BaseModel):
    application_id: int
    suggestion: str
