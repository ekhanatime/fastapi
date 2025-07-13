from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import Annotated
import secrets
import string

from ...core.db.database import async_get_db
from ...models.user import User
from ...schemas.lead_capture import LeadCaptureRequest, LeadCaptureResponse
from ...core.security import get_password_hash

router = APIRouter()


def generate_temporary_password(length: int = 12) -> str:
    """Generate a secure temporary password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@router.post("/capture-lead", response_model=LeadCaptureResponse)
async def capture_lead(
    lead_data: LeadCaptureRequest,
    db: Annotated[AsyncSession, Depends(async_get_db)]
):
    """Capture lead information and create user account with temporary password."""
    try:
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.email == lead_data.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            # For existing users, allow them to take new assessments without forcing login
            # Only show login modal if they explicitly want to access their dashboard/history
            return LeadCaptureResponse(
                success=True,
                message="Account found! You can take a new assessment or login to view your history.",
                user_id=str(existing_user.id),
                is_existing_user=False,  # Changed to False to allow direct assessment taking
                requires_password_change=False,
                show_login_option=True  # New field to show optional login button
            )
        
        # Generate temporary password
        temp_password = generate_temporary_password()
        hashed_password = get_password_hash(temp_password)
        
        # Create new user with temporary password
        new_user = User()
        new_user.email = lead_data.email
        new_user.hashed_password = hashed_password
        new_user.lead_status = "new"
        new_user.subscription_tier = "free"
        new_user.assessments_count = 0
        new_user.max_assessments = 3
        
        db.add(new_user)
        
        try:
            await db.commit()
            await db.refresh(new_user)
            
            return LeadCaptureResponse(
                success=True,
                message="Account created! Please save your temporary password and proceed with the assessment.",
                user_id=str(new_user.id),
                is_existing_user=False,
                temporary_password=temp_password,
                requires_password_change=True
            )
        except IntegrityError:
            # Handle race condition - user was created between our check and insert
            await db.rollback()
            
            # Fetch the existing user that was created by another request
            result = await db.execute(
                select(User).where(User.email == lead_data.email)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                return LeadCaptureResponse(
                    success=True,
                    message="Welcome back! You can proceed with the assessment.",
                    user_id=str(existing_user.id),
                    is_existing_user=True,
                    requires_password_change=False
                )
            else:
                # This should never happen, but just in case
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create or retrieve user account"
                )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create account: {str(e)}"
        )
