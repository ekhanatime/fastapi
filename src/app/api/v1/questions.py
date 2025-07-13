from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from ...core.db.database import async_get_db
from ...models.question import Question
from ...schemas.question import QuestionCreate, QuestionUpdate, QuestionResponse, QuestionList, QuestionWithOptions

router = APIRouter()


@router.get("/", response_model=QuestionList)
async def list_questions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(async_get_db)
):
    """List all questions with pagination and filtering."""
    query = select(Question)
    
    if category_id:
        query = query.filter(Question.category_id == category_id)
    if is_active is not None:
        query = query.filter(Question.is_active == is_active)
    
    questions = query.order_by(Question.display_order, Question.id).offset(skip).limit(limit).all()
    total = query.count()
    
    return QuestionList(
        questions=[QuestionResponse.from_orm(q) for q in questions],
        total=total
    )


@router.get("/{question_id}", response_model=QuestionWithOptions)
async def get_question(question_id: int, db: AsyncSession = Depends(async_get_db)):
    """Get a specific question by ID with its options."""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return QuestionWithOptions.from_orm(question)


@router.post("/", response_model=QuestionResponse, status_code=201)
async def create_question(question_data: QuestionCreate, db: AsyncSession = Depends(async_get_db)):
    """Create a new question."""
    # Verify category exists
    from app.models.category import Category
    category = db.query(Category).filter(Category.id == question_data.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")
    
    question = Question(**question_data.dict())
    db.add(question)
    db.commit()
    db.refresh(question)
    
    return QuestionResponse.from_orm(question)


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int, 
    question_data: QuestionUpdate, 
    db: AsyncSession = Depends(async_get_db)
):
    """Update an existing question."""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Verify category exists if being updated
    if question_data.category_id:
        from app.models.category import Category
        category = db.query(Category).filter(Category.id == question_data.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
    
    # Update only provided fields
    update_data = question_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(question, field, value)
    
    db.commit()
    db.refresh(question)
    
    return QuestionResponse.from_orm(question)


@router.delete("/{question_id}", status_code=204)
async def delete_question(question_id: int, db: AsyncSession = Depends(async_get_db)):
    """Delete a question and all its options."""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db.delete(question)
    db.commit()
    
    return None
