from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class LeadCreate(BaseModel):
    email: EmailStr = Field(..., description="Lead email address")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    company_name: Optional[str] = Field(None, max_length=255, description="Company name")
    job_title: Optional[str] = Field(None, max_length=255, description="Job title")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    company_size: Optional[str] = Field(None, description="Company size (small, medium, large)")
    industry: Optional[str] = Field(None, max_length=100, description="Industry")
    lead_source: Optional[str] = Field(None, max_length=100, description="Lead source")


class LeadResponse(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    lead_status: str
    lead_source: Optional[str] = None
    subscription_tier: str
    assessments_count: int
    max_assessments: int
    created_at: datetime

    class Config:
        from_attributes = True


class LeadUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    company_name: Optional[str] = Field(None, max_length=255, description="Company name")
    job_title: Optional[str] = Field(None, max_length=255, description="Job title")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    company_size: Optional[str] = Field(None, description="Company size")
    industry: Optional[str] = Field(None, max_length=100, description="Industry")
    lead_status: Optional[str] = Field(None, description="Lead status")
    lead_notes: Optional[str] = Field(None, description="Lead notes")


class EmailSubmissionResponse(BaseModel):
    message: str
    user_id: UUID
    can_take_assessment: bool
    assessments_remaining: int
