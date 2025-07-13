from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.db.database import async_get_db
from app.api.dependencies import get_current_admin_user
from app.models.user_profile import UserProfile
from app.models.assessment import Assessment
from app.models.customer_info import CustomerInfo

router = APIRouter(prefix="/admin/analytics", tags=["Admin - Analytics"])


@router.get("")
async def get_analytics(
    period: str = Query("30d", description="Time period: 7d, 30d, 90d, 1y"),
    db: AsyncSession = Depends(async_get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    """Get detailed analytics data (Admin only)"""
    
    # Calculate date range based on period
    now = datetime.utcnow()
    if period == "7d":
        start_date = now - timedelta(days=7)
    elif period == "30d":
        start_date = now - timedelta(days=30)
    elif period == "90d":
        start_date = now - timedelta(days=90)
    elif period == "1y":
        start_date = now - timedelta(days=365)
    else:
        start_date = now - timedelta(days=30)
    
    # Get total users in period
    users_query = select(func.count(UserProfile.user_id)).where(UserProfile.created_at >= start_date)
    users_result = await db.execute(users_query)
    total_users = users_result.scalar() or 0
    
    # Get total assessments in period
    assessments_query = select(func.count(Assessment.id)).where(Assessment.created_at >= start_date)
    assessments_result = await db.execute(assessments_query)
    total_assessments = assessments_result.scalar() or 0
    
    # Assessment completion rate
    users_with_assessments_query = select(func.count(func.distinct(Assessment.user_id))).where(
        and_(Assessment.created_at >= start_date, UserProfile.created_at >= start_date)
    ).select_from(Assessment.join(UserProfile, Assessment.user_id == UserProfile.user_id))
    users_with_assessments_result = await db.execute(users_with_assessments_query)
    users_with_assessments = users_with_assessments_result.scalar() or 0
    completion_rate = (users_with_assessments / total_users * 100) if total_users > 0 else 0
    
    # Average scores
    avg_score_query = select(func.avg(Assessment.overall_score)).where(Assessment.created_at >= start_date)
    avg_score_result = await db.execute(avg_score_query)
    avg_score = avg_score_result.scalar() or 0
    
    # Score distribution
    high_score_query = select(func.count(Assessment.id)).where(
        and_(Assessment.created_at >= start_date, Assessment.overall_score >= 80)
    )
    high_score_result = await db.execute(high_score_query)
    high_scores = high_score_result.scalar() or 0
    
    medium_score_query = select(func.count(Assessment.id)).where(
        and_(Assessment.created_at >= start_date, Assessment.overall_score >= 50, Assessment.overall_score < 80)
    )
    medium_score_result = await db.execute(medium_score_query)
    medium_scores = medium_score_result.scalar() or 0
    
    low_score_query = select(func.count(Assessment.id)).where(
        and_(Assessment.created_at >= start_date, Assessment.overall_score < 50)
    )
    low_score_result = await db.execute(low_score_query)
    low_scores = low_score_result.scalar() or 0
    
    # Interest in contact rate
    interested_query = select(func.count(Assessment.id)).where(
        and_(Assessment.created_at >= start_date, Assessment.interested_in_contact == True)
    )
    interested_result = await db.execute(interested_query)
    interested_count = interested_result.scalar() or 0
    interest_rate = (interested_count / total_assessments * 100) if total_assessments > 0 else 0
    
    # Daily trends (last 30 days)
    daily_data = []
    for i in range(30):
        day = now - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        daily_users_query = select(func.count(UserProfile.user_id)).where(
            and_(UserProfile.created_at >= day_start, UserProfile.created_at < day_end)
        )
        daily_users_result = await db.execute(daily_users_query)
        daily_users = daily_users_result.scalar() or 0
        
        daily_assessments_query = select(func.count(Assessment.id)).where(
            and_(Assessment.created_at >= day_start, Assessment.created_at < day_end)
        )
        daily_assessments_result = await db.execute(daily_assessments_query)
        daily_assessments = daily_assessments_result.scalar() or 0
        
        daily_data.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "users": daily_users,
            "assessments": daily_assessments
        })
    
    # Lead status distribution
    lead_status_query = select(CustomerInfo.lead_status, func.count(CustomerInfo.user_id)).group_by(CustomerInfo.lead_status)
    lead_status_result = await db.execute(lead_status_query)
    lead_status_data = {status: count for status, count in lead_status_result.fetchall()}
    
    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": now.isoformat(),
        "summary": {
            "total_users": total_users,
            "total_assessments": total_assessments,
            "completion_rate": round(completion_rate, 2),
            "average_score": round(float(avg_score), 2),
            "interest_rate": round(interest_rate, 2)
        },
        "score_distribution": {
            "high": high_scores,
            "medium": medium_scores,
            "low": low_scores
        },
        "lead_status_distribution": lead_status_data,
        "daily_trends": list(reversed(daily_data))  # Most recent first
    }


@router.get("/stats")
async def get_system_stats(
    db: AsyncSession = Depends(async_get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    """Get basic system statistics (Admin only)"""
    
    # Total counts
    total_users_query = select(func.count(UserProfile.user_id))
    total_users_result = await db.execute(total_users_query)
    total_users = total_users_result.scalar() or 0
    
    total_assessments_query = select(func.count(Assessment.id))
    total_assessments_result = await db.execute(total_assessments_query)
    total_assessments = total_assessments_result.scalar() or 0
    
    # Recent activity (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    
    recent_users_query = select(func.count(UserProfile.user_id)).where(UserProfile.created_at >= yesterday)
    recent_users_result = await db.execute(recent_users_query)
    recent_users = recent_users_result.scalar() or 0
    
    recent_assessments_query = select(func.count(Assessment.id)).where(Assessment.created_at >= yesterday)
    recent_assessments_result = await db.execute(recent_assessments_query)
    recent_assessments = recent_assessments_result.scalar() or 0
    
    # Average score
    avg_score_query = select(func.avg(Assessment.overall_score))
    avg_score_result = await db.execute(avg_score_query)
    avg_score = avg_score_result.scalar() or 0
    
    return {
        "total_users": total_users,
        "total_assessments": total_assessments,
        "recent_users_24h": recent_users,
        "recent_assessments_24h": recent_assessments,
        "average_score": round(float(avg_score), 2),
        "last_updated": datetime.utcnow().isoformat()
    }
