from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserProfileBase(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    company_name: Optional[str] = Field(None, max_length=255, description="Company name")
    job_title: Optional[str] = Field(None, max_length=255, description="Job title")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    company_size: Optional[str] = Field(None, description="Company size (small, medium, large)")
    industry: Optional[str] = Field(None, max_length=100, description="Industry")
    lead_source: Optional[str] = Field(None, max_length=100, description="Lead source")


class UserProfileCreate(UserProfileBase):
    user_id: int = Field(..., description="User ID from the main User table")


class UserProfileUpdate(UserProfileBase):
    lead_status: Optional[str] = Field(None, description="Lead status")
    lead_notes: Optional[str] = Field(None, description="Lead notes")
    subscription_tier: Optional[str] = Field(None, description="Subscription tier")


class UserProfileResponse(UserProfileBase):
    id: UUID
    user_id: int
    subscription_tier: str
    assessments_count: int
    max_assessments: int
    lead_status: str
    company_share_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LeadCaptureRequest(BaseModel):
    """For capturing leads without requiring full user registration"""
    email: EmailStr = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    company_name: Optional[str] = Field(None, max_length=255, description="Company name")
    job_title: Optional[str] = Field(None, max_length=255, description="Job title")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    company_size: Optional[str] = Field(None, description="Company size")
    industry: Optional[str] = Field(None, max_length=100, description="Industry")
    lead_source: Optional[str] = Field(None, max_length=100, description="Lead source")


class LeadCaptureResponse(BaseModel):
    message: str
    user_id: int
    profile_id: UUID
    can_take_assessment: bool
    assessments_remaining: int
    registration_required: bool = False  # True if they need to set a password
