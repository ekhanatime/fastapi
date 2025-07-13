from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from pydantic import BaseModel, UUID4
from decimal import Decimal

from ...core.db.database import async_get_db
from ...models.user_answer import UserAnswer
from ...api.dependencies import get_current_user
from ...models.user import User

router = APIRouter()


# Pydantic schemas
class UserAnswerBase(BaseModel):
    assessment_id: UUID4
    question_id: int
    selected_options: Optional[List[str]] = None
    is_correct: Optional[bool] = None
    points_earned: Optional[Decimal] = 0


class UserAnswerCreate(UserAnswerBase):
    pass


class UserAnswerUpdate(BaseModel):
    selected_options: Optional[List[str]] = None
    is_correct: Optional[bool] = None
    points_earned: Optional[Decimal] = None


class UserAnswerResponse(UserAnswerBase):
    id: UUID4
    
    class Config:
        from_attributes = True


@router.post("/", response_model=UserAnswerResponse, status_code=status.HTTP_201_CREATED)
async def create_user_answer(
    user_answer: UserAnswerCreate,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new user answer for an assessment question."""
    try:
        db_user_answer = UserAnswer(**user_answer.dict())
        db.add(db_user_answer)
        await db.commit()
        await db.refresh(db_user_answer)
        return db_user_answer
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating user answer: {str(e)}"
        )


@router.get("/assessment/{assessment_id}", response_model=List[UserAnswerResponse])
async def get_user_answers_by_assessment(
    assessment_id: UUID4,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all user answers for a specific assessment."""
    try:
        result = await db.execute(
            select(UserAnswer).where(UserAnswer.assessment_id == assessment_id)
        )
        user_answers = result.scalars().all()
        return user_answers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user answers: {str(e)}"
        )


@router.get("/{user_answer_id}", response_model=UserAnswerResponse)
async def get_user_answer(
    user_answer_id: UUID4,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific user answer by ID."""
    try:
        result = await db.execute(
            select(UserAnswer).where(UserAnswer.id == user_answer_id)
        )
        user_answer = result.scalar_one_or_none()
        
        if not user_answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User answer not found"
            )
        
        return user_answer
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user answer: {str(e)}"
        )


@router.put("/{user_answer_id}", response_model=UserAnswerResponse)
async def update_user_answer(
    user_answer_id: UUID4,
    user_answer_update: UserAnswerUpdate,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a user answer."""
    try:
        result = await db.execute(
            select(UserAnswer).where(UserAnswer.id == user_answer_id)
        )
        db_user_answer = result.scalar_one_or_none()
        
        if not db_user_answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User answer not found"
            )
        
        # Update fields
        update_data = user_answer_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user_answer, field, value)
        
        await db.commit()
        await db.refresh(db_user_answer)
        return db_user_answer
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating user answer: {str(e)}"
        )


@router.delete("/{user_answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_answer(
    user_answer_id: UUID4,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a user answer."""
    try:
        result = await db.execute(
            select(UserAnswer).where(UserAnswer.id == user_answer_id)
        )
        db_user_answer = result.scalar_one_or_none()
        
        if not db_user_answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User answer not found"
            )
        
        await db.execute(delete(UserAnswer).where(UserAnswer.id == user_answer_id))
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user answer: {str(e)}"
        )
