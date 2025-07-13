from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from app.core.db.database import async_get_db
from app.core.security import create_access_token, verify_password
from app.models.user_profile import UserProfile
from app.schemas.admin import AdminAuthRequest, AdminAuthResponse
from app.core.config import settings
from app.api.dependencies import get_current_admin_user

router = APIRouter(prefix="/admin/auth", tags=["Admin - Authentication"])


@router.post("/login", response_model=AdminAuthResponse)
async def admin_login(
    auth_data: AdminAuthRequest,
    db: AsyncSession = Depends(async_get_db)
):
    """Admin login endpoint"""
    
    # Get user by username/email
    user_query = select(UserProfile).where(
        (UserProfile.email == auth_data.username) | 
        (UserProfile.username == auth_data.username)
    )
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if user is superuser/admin
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    # Verify password
    if not verify_password(auth_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return AdminAuthResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/verify")
async def verify_admin_token(
    current_user: dict = Depends(get_current_admin_user)
):
    """Verify admin token validity"""
    return {
        "valid": True,
        "user_id": current_user["id"],
        "email": current_user["email"],
        "is_superuser": current_user["is_superuser"]
    }
