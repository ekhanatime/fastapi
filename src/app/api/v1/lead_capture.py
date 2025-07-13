from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated

from app.core.database import async_get_db
from app.models.user import User
from app.models.user_profile import UserProfile
from app.schemas.user_profile import LeadCaptureRequest, LeadCaptureResponse
from app.schemas.user import UserCreate, UserCreateInternal
from app.core.security import get_password_hash
from app.crud.crud_users import crud_users
import secrets
import string

router = APIRouter()


@router.post("/capture-lead", response_model=LeadCaptureResponse)
async def capture_lead(
    lead_data: LeadCaptureRequest, 
    db: Annotated[AsyncSession, Depends(async_get_db)]
):
    """
    Capture lead information and create user account if needed.
    Works with existing authentication system.
    """
    # Check if user already exists
    existing_user = await crud_users.get(db=db, email=lead_data.email, is_deleted=False)
    
    if existing_user:
        # User exists, get or create their profile
        user_id = existing_user["id"]
        
        # Check if profile exists
        result = await db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if profile:
            # Update existing profile with new information
            if lead_data.full_name and not profile.full_name:
                profile.full_name = lead_data.full_name
            if lead_data.company_name and not profile.company_name:
                profile.company_name = lead_data.company_name
            if lead_data.job_title and not profile.job_title:
                profile.job_title = lead_data.job_title
            if lead_data.phone and not profile.phone:
                profile.phone = lead_data.phone
            if lead_data.company_size and not profile.company_size:
                profile.company_size = lead_data.company_size
            if lead_data.industry and not profile.industry:
                profile.industry = lead_data.industry
            if lead_data.lead_source and not profile.lead_source:
                profile.lead_source = lead_data.lead_source
            
            await db.commit()
            await db.refresh(profile)
        else:
            # Create new profile for existing user
            profile_data = lead_data.dict(exclude={"email"})
            profile_data["user_id"] = user_id
            profile = UserProfile(**profile_data)
            db.add(profile)
            await db.commit()
            await db.refresh(profile)
        
        message = "Welcome back! You can continue taking assessments."
        registration_required = False
        
    else:
        # Create new user with temporary password
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        # Extract name from email if full_name not provided
        display_name = lead_data.full_name or lead_data.email.split('@')[0]
        username = lead_data.email.split('@')[0].lower()[:20]  # Ensure username length limit
        
        # Create user via existing CRUD
        user_create = UserCreateInternal(
            name=display_name,
            username=username,
            email=lead_data.email,
            hashed_password=get_password_hash(temp_password)
        )
        
        created_user = await crud_users.create(db=db, object=user_create)
        user_id = created_user.id
        
        # Create user profile
        profile_data = lead_data.dict(exclude={"email"})
        profile_data["user_id"] = user_id
        profile = UserProfile(**profile_data)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        
        message = "Thank you for your interest! You can now take your security assessment."
        registration_required = True  # They'll need to set a proper password later
    
    # Check assessment limits
    can_take_assessment = profile.assessments_count < profile.max_assessments
    assessments_remaining = max(0, profile.max_assessments - profile.assessments_count)
    
    return LeadCaptureResponse(
        message=message,
        user_id=user_id,
        profile_id=profile.id,
        can_take_assessment=can_take_assessment,
        assessments_remaining=assessments_remaining,
        registration_required=registration_required
    )
