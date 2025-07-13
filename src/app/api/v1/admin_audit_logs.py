from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime, timedelta
import math

from app.core.db.database import async_get_db
from app.api.dependencies import get_current_admin_user
from app.models.assessment import Assessment
from app.models.user_profile import UserProfile
from app.schemas.admin import PaginatedResponse

router = APIRouter(prefix="/admin/audit-logs", tags=["Admin - Audit Logs"])


@router.get("", response_model=PaginatedResponse)
async def get_audit_logs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    user_email: Optional[str] = Query(None, description="Filter by user email"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date"),
    db: AsyncSession = Depends(async_get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    """Get audit logs with pagination and filtering (Admin only)"""
    
    # This is a placeholder implementation since there's no dedicated audit_logs table
    # In a real system, you would have an audit_logs table to track all user actions
    
    # For now, we'll generate audit logs from existing data (assessments, user registrations, etc.)
    audit_logs = []
    
    # Get recent assessments as audit events
    assessments_query = select(Assessment, UserProfile.email).join(
        UserProfile, Assessment.user_id == UserProfile.user_id
    ).order_by(Assessment.created_at.desc()).limit(100)
    
    assessments_result = await db.execute(assessments_query)
    assessments_data = assessments_result.fetchall()
    
    for assessment, user_email in assessments_data:
        audit_log = {
            "id": f"assessment_{assessment.id}",
            "timestamp": assessment.created_at,
            "action": "assessment_submitted",
            "user_email": user_email,
            "ip_address": str(assessment.submission_ip) if assessment.submission_ip else "Unknown",
            "user_agent": assessment.user_agent or "Unknown",
            "details": {
                "assessment_id": str(assessment.id),
                "overall_score": assessment.overall_score,
                "total_score": assessment.total_score,
                "max_score": assessment.max_score,
                "interested_in_contact": assessment.interested_in_contact
            }
        }
        audit_logs.append(audit_log)
    
    # Get recent user registrations as audit events
    users_query = select(UserProfile).order_by(UserProfile.created_at.desc()).limit(50)
    users_result = await db.execute(users_query)
    users_data = users_result.scalars().all()
    
    for user in users_data:
        audit_log = {
            "id": f"user_registered_{user.user_id}",
            "timestamp": user.created_at,
            "action": "user_registered",
            "user_email": user.email,
            "ip_address": "Unknown",  # Would need to track this during registration
            "user_agent": "Unknown",  # Would need to track this during registration
            "details": {
                "user_id": user.user_id,
                "registration_method": "email"
            }
        }
        audit_logs.append(audit_log)
    
    # Sort all logs by timestamp (most recent first)
    audit_logs.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Apply filters
    filtered_logs = audit_logs
    
    if action:
        filtered_logs = [log for log in filtered_logs if log["action"] == action]
    
    if user_email:
        filtered_logs = [log for log in filtered_logs if user_email.lower() in log["user_email"].lower()]
    
    if date_from:
        filtered_logs = [log for log in filtered_logs if log["timestamp"] >= date_from]
    
    if date_to:
        filtered_logs = [log for log in filtered_logs if log["timestamp"] <= date_to]
    
    # Apply pagination
    total = len(filtered_logs)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_logs = filtered_logs[start_idx:end_idx]
    
    total_pages = math.ceil(total / page_size)
    
    return PaginatedResponse(
        items=paginated_logs,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/actions")
async def get_available_actions(
    admin_user: dict = Depends(get_current_admin_user)
):
    """Get list of available audit log action types (Admin only)"""
    
    return {
        "actions": [
            "assessment_submitted",
            "user_registered",
            "user_login",
            "user_logout",
            "admin_login",
            "settings_updated",
            "customer_updated",
            "question_created",
            "question_updated",
            "question_deleted",
            "category_created",
            "category_updated",
            "category_deleted"
        ]
    }


@router.get("/summary")
async def get_audit_summary(
    days: int = Query(7, ge=1, le=365, description="Number of days to summarize"),
    db: AsyncSession = Depends(async_get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    """Get audit log summary for the specified period (Admin only)"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Count assessments in period
    assessments_query = select(Assessment).where(Assessment.created_at >= start_date)
    assessments_result = await db.execute(assessments_query)
    assessments_count = len(assessments_result.scalars().all())
    
    # Count user registrations in period
    users_query = select(UserProfile).where(UserProfile.created_at >= start_date)
    users_result = await db.execute(users_query)
    users_count = len(users_result.scalars().all())
    
    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": datetime.utcnow().isoformat(),
        "summary": {
            "total_events": assessments_count + users_count,
            "assessment_submissions": assessments_count,
            "user_registrations": users_count,
            "admin_actions": 0,  # Would track from dedicated audit table
            "system_events": 0   # Would track from dedicated audit table
        }
    }
