from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import func

from ...core.db.database import async_get_db
from ...models.user import User
from ...schemas.lead import LeadCreate, LeadResponse, EmailSubmissionResponse

router = APIRouter()


@router.post("/submit-email", response_model=EmailSubmissionResponse)
async def submit_email(lead_data: LeadCreate, db: AsyncSession = Depends(async_get_db)):
    """
    Submit email to capture lead and allow assessment taking.
    Creates a new lead or updates existing one.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == lead_data.email).first()
    
    if existing_user:
        # Update existing user with new information if provided
        if lead_data.full_name and not existing_user.full_name:
            existing_user.full_name = lead_data.full_name
        if lead_data.company_name and not existing_user.company_name:
            existing_user.company_name = lead_data.company_name
        if lead_data.job_title and not existing_user.job_title:
            existing_user.job_title = lead_data.job_title
        if lead_data.phone and not existing_user.phone:
            existing_user.phone = lead_data.phone
        if lead_data.company_size and not existing_user.company_size:
            existing_user.company_size = lead_data.company_size
        if lead_data.industry and not existing_user.industry:
            existing_user.industry = lead_data.industry
        if lead_data.lead_source and not existing_user.lead_source:
            existing_user.lead_source = lead_data.lead_source
        
        existing_user.updated_at = func.now()
        db.commit()
        db.refresh(existing_user)
        
        user = existing_user
        message = "Welcome back! You can continue taking assessments."
    else:
        # Create new lead
        user_data = lead_data.dict()
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        
        message = "Thank you for your interest! You can now take your security assessment."
    
    # Check if user can take more assessments
    can_take_assessment = user.assessments_count < user.max_assessments
    assessments_remaining = max(0, user.max_assessments - user.assessments_count)
    
    return EmailSubmissionResponse(
        message=message,
        user_id=user.id,
        can_take_assessment=can_take_assessment,
        assessments_remaining=assessments_remaining
    )


@router.get("/{user_id}", response_model=LeadResponse)
async def get_lead(user_id: str, db: AsyncSession = Depends(async_get_db)):
    """Get lead information by user ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return LeadResponse.from_orm(user)
