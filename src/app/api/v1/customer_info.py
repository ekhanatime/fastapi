from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from pydantic import BaseModel, UUID4
from datetime import datetime
from enum import Enum

from ...core.db.database import async_get_db
from ...models.customer_info import CustomerInfo, LeadStatusEnum
from ...api.dependencies import get_current_user
from ...models.user import User

router = APIRouter()


# Pydantic schemas
class LeadStatusResponse(str, Enum):
    NEW = "New"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    CUSTOMER = "Customer"


class CustomerInfoBase(BaseModel):
    company_name: Optional[str] = None
    phone_number: Optional[str] = None
    job_title: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    notes: Optional[str] = None
    lead_source: Optional[str] = None
    lead_status: Optional[LeadStatusResponse] = LeadStatusResponse.NEW
    assigned_to: Optional[str] = None
    subscription_plan: Optional[str] = "free"
    max_submissions: Optional[int] = 1
    used_submissions: Optional[int] = 0
    subscription_expires_at: Optional[datetime] = None
    payment_status: Optional[str] = "active"


class CustomerInfoCreate(CustomerInfoBase):
    user_id: UUID4


class CustomerInfoUpdate(CustomerInfoBase):
    pass


class CustomerInfoResponse(CustomerInfoBase):
    id: UUID4
    user_id: UUID4
    company_share_token: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


@router.post("/", response_model=CustomerInfoResponse, status_code=status.HTTP_201_CREATED)
async def create_customer_info(
    customer_info: CustomerInfoCreate,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Create customer info for a user."""
    try:
        db_customer_info = CustomerInfo(**customer_info.dict())
        db.add(db_customer_info)
        await db.commit()
        await db.refresh(db_customer_info)
        return db_customer_info
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating customer info: {str(e)}"
        )


@router.get("/", response_model=List[CustomerInfoResponse])
async def get_all_customer_info(
    skip: int = 0,
    limit: int = 100,
    lead_status: Optional[LeadStatusResponse] = None,
    subscription_plan: Optional[str] = None,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all customer info with optional filtering."""
    try:
        query = select(CustomerInfo)
        
        if lead_status:
            query = query.where(CustomerInfo.lead_status == lead_status)
        if subscription_plan:
            query = query.where(CustomerInfo.subscription_plan == subscription_plan)
            
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        customer_infos = result.scalars().all()
        return customer_infos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching customer info: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=CustomerInfoResponse)
async def get_customer_info_by_user(
    user_id: UUID4,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Get customer info for a specific user."""
    try:
        result = await db.execute(
            select(CustomerInfo).where(CustomerInfo.user_id == user_id)
        )
        customer_info = result.scalar_one_or_none()
        
        if not customer_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer info not found"
            )
        
        return customer_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching customer info: {str(e)}"
        )


@router.get("/{customer_info_id}", response_model=CustomerInfoResponse)
async def get_customer_info(
    customer_info_id: UUID4,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Get customer info by ID."""
    try:
        result = await db.execute(
            select(CustomerInfo).where(CustomerInfo.id == customer_info_id)
        )
        customer_info = result.scalar_one_or_none()
        
        if not customer_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer info not found"
            )
        
        return customer_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching customer info: {str(e)}"
        )


@router.put("/{customer_info_id}", response_model=CustomerInfoResponse)
async def update_customer_info(
    customer_info_id: UUID4,
    customer_info_update: CustomerInfoUpdate,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Update customer info."""
    try:
        result = await db.execute(
            select(CustomerInfo).where(CustomerInfo.id == customer_info_id)
        )
        db_customer_info = result.scalar_one_or_none()
        
        if not db_customer_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer info not found"
            )
        
        # Update fields
        update_data = customer_info_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_customer_info, field, value)
        
        await db.commit()
        await db.refresh(db_customer_info)
        return db_customer_info
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating customer info: {str(e)}"
        )


@router.delete("/{customer_info_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer_info(
    customer_info_id: UUID4,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete customer info."""
    try:
        result = await db.execute(
            select(CustomerInfo).where(CustomerInfo.id == customer_info_id)
        )
        db_customer_info = result.scalar_one_or_none()
        
        if not db_customer_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer info not found"
            )
        
        await db.execute(delete(CustomerInfo).where(CustomerInfo.id == customer_info_id))
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting customer info: {str(e)}"
        )


@router.post("/{customer_info_id}/increment-submissions", response_model=CustomerInfoResponse)
async def increment_submissions(
    customer_info_id: UUID4,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Increment used submissions for a customer."""
    try:
        result = await db.execute(
            select(CustomerInfo).where(CustomerInfo.id == customer_info_id)
        )
        db_customer_info = result.scalar_one_or_none()
        
        if not db_customer_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer info not found"
            )
        
        if db_customer_info.used_submissions >= db_customer_info.max_submissions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum submissions reached for this subscription plan"
            )
        
        db_customer_info.used_submissions += 1
        await db.commit()
        await db.refresh(db_customer_info)
        return db_customer_info
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error incrementing submissions: {str(e)}"
        )
