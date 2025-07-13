from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import datetime
import math

from app.core.db.database import async_get_db
from app.api.dependencies import get_current_admin_user
from app.models.user_profile import UserProfile
from app.models.assessment import Assessment
from app.models.customer_info import CustomerInfo
from app.schemas.admin import PaginatedResponse, CustomerDetailResponse

router = APIRouter(prefix="/admin/customers", tags=["Admin - Customers"])


@router.get("", response_model=PaginatedResponse)
async def get_customers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search in email, company name"),
    lead_status: Optional[str] = Query(None, description="Filter by lead status"),
    company_size: Optional[str] = Query(None, description="Filter by company size"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    db: AsyncSession = Depends(async_get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    """Get customers with pagination and filtering (Admin only)"""
    
    # Build query
    query = select(UserProfile).join(CustomerInfo, UserProfile.user_id == CustomerInfo.user_id, isouter=True)
    
    # Apply filters
    conditions = []
    if search:
        conditions.append(
            UserProfile.email.ilike(f"%{search}%") |
            CustomerInfo.company_name.ilike(f"%{search}%")
        )
    if lead_status:
        conditions.append(CustomerInfo.lead_status == lead_status)
    if company_size:
        conditions.append(CustomerInfo.company_size == company_size)
    if industry:
        conditions.append(CustomerInfo.industry == industry)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    skip = (page - 1) * page_size
    query = query.offset(skip).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    users = result.scalars().all()
    
    # Transform to response format
    customer_responses = []
    for user in users:
        # Get assessment stats
        assessment_count_query = select(func.count(Assessment.id)).where(Assessment.user_id == user.user_id)
        assessment_count_result = await db.execute(assessment_count_query)
        total_assessments = assessment_count_result.scalar() or 0
        
        avg_score_query = select(func.avg(Assessment.overall_score)).where(Assessment.user_id == user.user_id)
        avg_score_result = await db.execute(avg_score_query)
        avg_score = avg_score_result.scalar()
        
        # Get last assessment date
        last_assessment_query = select(Assessment.created_at).where(Assessment.user_id == user.user_id).order_by(Assessment.created_at.desc()).limit(1)
        last_assessment_result = await db.execute(last_assessment_query)
        last_assessment_date = last_assessment_result.scalar()
        
        customer_response = {
            "id": user.user_id,
            "email": user.email,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "customer_info": user.customer_info,
            "total_assessments": total_assessments,
            "avg_score": float(avg_score) if avg_score else None,
            "last_assessment_date": last_assessment_date
        }
        customer_responses.append(customer_response)
    
    total_pages = math.ceil(total / page_size)
    
    return PaginatedResponse(
        items=customer_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{user_id}", response_model=CustomerDetailResponse)
async def get_customer_detail(
    user_id: str,
    db: AsyncSession = Depends(async_get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    """Get detailed customer information (Admin only)"""
    
    # Get user profile
    user_query = select(UserProfile).where(UserProfile.user_id == user_id)
    user_result = await db.execute(user_query)
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get customer assessments
    assessments_query = select(Assessment).where(Assessment.user_id == user_id).order_by(Assessment.created_at.desc()).limit(10)
    assessments_result = await db.execute(assessments_query)
    assessments = assessments_result.scalars().all()
    
    # Calculate stats
    total_assessments = len(assessments)
    avg_score = sum(a.overall_score for a in assessments) / total_assessments if assessments else 0
    
    return CustomerDetailResponse(
        id=user.user_id,
        email=user.email,
        created_at=user.created_at,
        updated_at=user.updated_at,
        customer_info=user.customer_info,
        total_assessments=total_assessments,
        avg_score=avg_score,
        assessments=[{
            "id": str(a.id),
            "overall_score": a.overall_score,
            "total_score": a.total_score,
            "max_score": a.max_score,
            "interested_in_contact": a.interested_in_contact,
            "created_at": a.created_at
        } for a in assessments]
    )


@router.put("/{user_id}")
async def update_customer(
    user_id: str,
    customer_update: dict,
    db: AsyncSession = Depends(async_get_db),
    admin_user: dict = Depends(get_current_admin_user)
):
    """Update customer information (Admin only)"""
    
    # Get customer info
    customer_query = select(CustomerInfo).where(CustomerInfo.user_id == user_id)
    customer_result = await db.execute(customer_query)
    customer_info = customer_result.scalar_one_or_none()
    
    if not customer_info:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Update customer info
    for key, value in customer_update.items():
        if hasattr(customer_info, key):
            setattr(customer_info, key, value)
    
    customer_info.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(customer_info)
    
    return {"message": "Customer updated successfully", "customer_id": user_id}
