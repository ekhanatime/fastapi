from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from pydantic import BaseModel, UUID4
from decimal import Decimal

from ...core.db.database import async_get_db
from ...models.category_score import CategoryScore
from ...api.dependencies import get_current_user
from ...models.user import User

router = APIRouter()


# Pydantic schemas
class CategoryScoreBase(BaseModel):
    assessment_id: UUID4
    category_id: str
    score: Optional[Decimal] = None
    max_score: Optional[Decimal] = None
    questions_count: Optional[int] = None
    percentage: Optional[int] = None


class CategoryScoreCreate(CategoryScoreBase):
    pass


class CategoryScoreUpdate(BaseModel):
    score: Optional[Decimal] = None
    max_score: Optional[Decimal] = None
    questions_count: Optional[int] = None
    percentage: Optional[int] = None


class CategoryScoreResponse(CategoryScoreBase):
    id: UUID4
    
    class Config:
        from_attributes = True


@router.post("/", response_model=CategoryScoreResponse, status_code=status.HTTP_201_CREATED)
async def create_category_score(
    category_score: CategoryScoreCreate,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new category score for an assessment."""
    try:
        db_category_score = CategoryScore(**category_score.dict())
        db.add(db_category_score)
        await db.commit()
        await db.refresh(db_category_score)
        return db_category_score
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating category score: {str(e)}"
        )


@router.get("/assessment/{assessment_id}", response_model=List[CategoryScoreResponse])
async def get_category_scores_by_assessment(
    assessment_id: UUID4,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all category scores for a specific assessment."""
    try:
        result = await db.execute(
            select(CategoryScore).where(CategoryScore.assessment_id == assessment_id)
        )
        category_scores = result.scalars().all()
        return category_scores
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching category scores: {str(e)}"
        )


@router.get("/{category_score_id}", response_model=CategoryScoreResponse)
async def get_category_score(
    category_score_id: UUID4,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific category score by ID."""
    try:
        result = await db.execute(
            select(CategoryScore).where(CategoryScore.id == category_score_id)
        )
        category_score = result.scalar_one_or_none()
        
        if not category_score:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category score not found"
            )
        
        return category_score
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching category score: {str(e)}"
        )


@router.put("/{category_score_id}", response_model=CategoryScoreResponse)
async def update_category_score(
    category_score_id: UUID4,
    category_score_update: CategoryScoreUpdate,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a category score."""
    try:
        result = await db.execute(
            select(CategoryScore).where(CategoryScore.id == category_score_id)
        )
        db_category_score = result.scalar_one_or_none()
        
        if not db_category_score:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category score not found"
            )
        
        # Update fields
        update_data = category_score_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category_score, field, value)
        
        await db.commit()
        await db.refresh(db_category_score)
        return db_category_score
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating category score: {str(e)}"
        )


@router.delete("/{category_score_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category_score(
    category_score_id: UUID4,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a category score."""
    try:
        result = await db.execute(
            select(CategoryScore).where(CategoryScore.id == category_score_id)
        )
        db_category_score = result.scalar_one_or_none()
        
        if not db_category_score:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category score not found"
            )
        
        await db.execute(delete(CategoryScore).where(CategoryScore.id == category_score_id))
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting category score: {str(e)}"
        )
