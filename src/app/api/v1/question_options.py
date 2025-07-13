from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from ...core.db.database import async_get_db
from ...models.question_option import QuestionOption
from ...schemas.question_option import QuestionOptionCreate, QuestionOptionUpdate, QuestionOptionResponse, QuestionOptionList

router = APIRouter()


@router.get("/", response_model=QuestionOptionList)
async def list_question_options(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    question_id: Optional[int] = Query(None, description="Filter by question ID"),
    db: AsyncSession = Depends(async_get_db)
):
    """List all question options with pagination and filtering."""
    query = db.query(QuestionOption)
    
    if question_id:
        query = query.filter(QuestionOption.question_id == question_id)
    
    options = query.order_by(QuestionOption.display_order, QuestionOption.id).offset(skip).limit(limit).all()
    total = query.count()
    
    return QuestionOptionList(
        options=[QuestionOptionResponse.from_orm(opt) for opt in options],
        total=total
    )


@router.get("/{option_id}", response_model=QuestionOptionResponse)
async def get_question_option(option_id: int, db: AsyncSession = Depends(async_get_db)):
    """Get a specific question option by ID."""
    option = db.query(QuestionOption).filter(QuestionOption.id == option_id).first()
    if not option:
        raise HTTPException(status_code=404, detail="Question option not found")
    
    return QuestionOptionResponse.from_orm(option)


@router.post("/", response_model=QuestionOptionResponse, status_code=201)
async def create_question_option(option_data: QuestionOptionCreate, db: AsyncSession = Depends(async_get_db)):
    """Create a new question option."""
    # Verify question exists
    from app.models.question import Question
    question = db.query(Question).filter(Question.id == option_data.question_id).first()
    if not question:
        raise HTTPException(status_code=400, detail="Question not found")
    
    option = QuestionOption(**option_data.dict())
    db.add(option)
    db.commit()
    db.refresh(option)
    
    return QuestionOptionResponse.from_orm(option)


@router.put("/{option_id}", response_model=QuestionOptionResponse)
async def update_question_option(
    option_id: int, 
    option_data: QuestionOptionUpdate, 
    db: AsyncSession = Depends(async_get_db)
):
    """Update an existing question option."""
    option = db.query(QuestionOption).filter(QuestionOption.id == option_id).first()
    if not option:
        raise HTTPException(status_code=404, detail="Question option not found")
    
    # Verify question exists if being updated
    if option_data.question_id:
        from app.models.question import Question
        question = db.query(Question).filter(Question.id == option_data.question_id).first()
        if not question:
            raise HTTPException(status_code=400, detail="Question not found")
    
    # Update only provided fields
    update_data = option_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(option, field, value)
    
    db.commit()
    db.refresh(option)
    
    return QuestionOptionResponse.from_orm(option)


@router.delete("/{option_id}", status_code=204)
async def delete_question_option(option_id: int, db: AsyncSession = Depends(async_get_db)):
    """Delete a question option."""
    option = db.query(QuestionOption).filter(QuestionOption.id == option_id).first()
    if not option:
        raise HTTPException(status_code=404, detail="Question option not found")
    
    db.delete(option)
    db.commit()
    
    return None
