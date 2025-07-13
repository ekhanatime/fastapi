from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any

from app.core.db.database import async_get_db
from app.api.dependencies import get_current_admin_user
from app.core.config import settings

router = APIRouter(prefix="/admin/settings", tags=["Admin - Settings"])


@router.get("")
async def get_system_settings(
    db: AsyncSession = Depends(async_get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    """Get system settings (Admin only)"""
    
    # Return current system settings
    # In a real implementation, these would be stored in a settings table
    return {
        "email_notifications_enabled": True,
        "max_assessments_per_user": 10,
        "assessment_timeout_minutes": 30,
        "company_share_token_expiry_days": 30,
        "max_company_submissions": 100,
        "maintenance_mode": False,
        "registration_enabled": True,
        "anonymous_submissions_enabled": True,
        "admin_interface_enabled": settings.CRUD_ADMIN_ENABLED,
        "redis_enabled": settings.CRUD_ADMIN_REDIS_ENABLED,
        "session_timeout_minutes": settings.CRUD_ADMIN_SESSION_TIMEOUT,
        "max_sessions_per_user": settings.CRUD_ADMIN_MAX_SESSIONS,
        "track_events": settings.CRUD_ADMIN_TRACK_EVENTS,
        "track_sessions_in_db": settings.CRUD_ADMIN_TRACK_SESSIONS
    }


@router.put("")
async def update_system_settings(
    settings_update: Dict[str, Any],
    db: AsyncSession = Depends(async_get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    """Update system settings (Admin only)"""
    
    # Validate settings
    allowed_settings = {
        "email_notifications_enabled",
        "max_assessments_per_user", 
        "assessment_timeout_minutes",
        "company_share_token_expiry_days",
        "max_company_submissions",
        "maintenance_mode",
        "registration_enabled",
        "anonymous_submissions_enabled"
    }
    
    invalid_settings = set(settings_update.keys()) - allowed_settings
    if invalid_settings:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid settings: {list(invalid_settings)}"
        )
    
    # In a real implementation, you would:
    # 1. Validate the setting values
    # 2. Update the settings in the database
    # 3. Apply the settings to the running application
    
    # For now, just return success
    return {
        "message": "Settings updated successfully", 
        "updated_settings": settings_update
    }


@router.get("/environment")
async def get_environment_info(
    admin_user: dict = Depends(get_current_admin_user)
):
    """Get environment information (Admin only)"""
    
    return {
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "database_url": settings.DATABASE_URL[:20] + "..." if settings.DATABASE_URL else None,
        "redis_enabled": settings.CRUD_ADMIN_REDIS_ENABLED,
        "admin_mount_path": settings.CRUD_ADMIN_MOUNT_PATH,
        "cors_origins": settings.CORS_ORIGINS,
        "version": "1.0.0"  # You could get this from a version file
    }
