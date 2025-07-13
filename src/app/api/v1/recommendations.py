from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from pydantic import BaseModel, UUID4
from enum import Enum

from ...core.db.database import async_get_db
from ...models.recommendation import Recommendation, PriorityEnum
from ...api.dependencies import get_current_user
from ...models.user import User

router = APIRouter()


# Pydantic schemas
class PriorityResponse(str, Enum):
    KRITISK = "Kritisk"
    HOY = "Høy"
    MIDDELS = "Middels"
    LAV = "Lav"


class RecommendationBase(BaseModel):
    assessment_id: UUID4
    category_id: str
    priority: Optional[PriorityResponse] = None
    recommendation: Optional[str] = None
    action_items: Optional[List[str]] = None


class RecommendationCreate(RecommendationBase):
    pass


class RecommendationUpdate(BaseModel):
    priority: Optional[PriorityResponse] = None
    recommendation: Optional[str] = None
    action_items: Optional[List[str]] = None


class RecommendationResponse(RecommendationBase):
    id: UUID4
    
    class Config:
        from_attributes = True


@router.post("/", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
async def create_recommendation(
    recommendation: RecommendationCreate,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new recommendation for an assessment."""
    try:
        db_recommendation = Recommendation(**recommendation.dict())
        db.add(db_recommendation)
        await db.commit()
        await db.refresh(db_recommendation)
        return db_recommendation
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating recommendation: {str(e)}"
        )


@router.get("/assessment/{assessment_id}", response_model=List[RecommendationResponse])
async def get_recommendations_by_assessment(
    assessment_id: UUID4,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all recommendations for a specific assessment."""
    try:
        result = await db.execute(
            select(Recommendation).where(Recommendation.assessment_id == assessment_id)
        )
        recommendations = result.scalars().all()
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching recommendations: {str(e)}"
        )


@router.get("/category/{category_id}", response_model=List[RecommendationResponse])
async def get_recommendations_by_category(
    category_id: str,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all recommendations for a specific category."""
    try:
        result = await db.execute(
            select(Recommendation).where(Recommendation.category_id == category_id)
        )
        recommendations = result.scalars().all()
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching recommendations: {str(e)}"
        )


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
async def get_recommendation(
    recommendation_id: UUID4,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific recommendation by ID."""
    try:
        result = await db.execute(
            select(Recommendation).where(Recommendation.id == recommendation_id)
        )
        recommendation = result.scalar_one_or_none()
        
        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommendation not found"
            )
        
        return recommendation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching recommendation: {str(e)}"
        )


@router.put("/{recommendation_id}", response_model=RecommendationResponse)
async def update_recommendation(
    recommendation_id: UUID4,
    recommendation_update: RecommendationUpdate,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a recommendation."""
    try:
        result = await db.execute(
            select(Recommendation).where(Recommendation.id == recommendation_id)
        )
        db_recommendation = result.scalar_one_or_none()
        
        if not db_recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommendation not found"
            )
        
        # Update fields
        update_data = recommendation_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_recommendation, field, value)
        
        await db.commit()
        await db.refresh(db_recommendation)
        return db_recommendation
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating recommendation: {str(e)}"
        )


@router.delete("/{recommendation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recommendation(
    recommendation_id: UUID4,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a recommendation."""
    try:
        result = await db.execute(
            select(Recommendation).where(Recommendation.id == recommendation_id)
        )
        db_recommendation = result.scalar_one_or_none()
        
        if not db_recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommendation not found"
            )
        
        await db.execute(delete(Recommendation).where(Recommendation.id == recommendation_id))
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting recommendation: {str(e)}"
        )
