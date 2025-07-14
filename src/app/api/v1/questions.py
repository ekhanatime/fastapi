from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
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
    count_query = select(func.count()).select_from(Question)

    if category_id:
        query = query.where(Question.category_id == category_id)
        count_query = count_query.where(Question.category_id == category_id)

    if is_active is not None:
        query = query.where(Question.is_active == is_active)
        count_query = count_query.where(Question.is_active == is_active)

    # Execute the count query
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Execute the main query for the data
    query = query.order_by(Question.display_order, Question.id).offset(skip).limit(limit)
    result = await db.execute(query)
    questions = result.scalars().all()

    return QuestionList(
        questions=[QuestionResponse.from_orm(q) for q in questions],
        total=total
    )


@router.get("/{question_id}", response_model=QuestionWithOptions)
async def get_question(question_id: int, db: AsyncSession = Depends(async_get_db)):
    """Get a specific question by ID with its options."""
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalars().first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return QuestionWithOptions.from_orm(question)


@router.post("/", response_model=QuestionResponse, status_code=201)
async def create_question(question_data: QuestionCreate, db: AsyncSession = Depends(async_get_db)):
    """Create a new question."""
    # Verify category exists
    from ...models.category import Category
    result = await db.execute(select(Category).where(Category.id == question_data.category_id))
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")
    
    question = Question(**question_data.dict())
    db.add(question)
    await db.commit()
    await db.refresh(question)
    
    return QuestionResponse.from_orm(question)


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int, 
    question_data: QuestionUpdate, 
    db: AsyncSession = Depends(async_get_db)
):
    """Update an existing question."""
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalars().first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Verify category exists if being updated
    if question_data.category_id:
        from ...models.category import Category
        result = await db.execute(select(Category).where(Category.id == question_data.category_id))
        category = result.scalars().first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
    
    # Update only provided fields
    update_data = question_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(question, field, value)
    
    await db.commit()
    await db.refresh(question)
    
    return QuestionResponse.from_orm(question)


@router.delete("/{question_id}", status_code=204)
async def delete_question(question_id: int, db: AsyncSession = Depends(async_get_db)):
    """Delete a question and all its options."""
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalars().first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    await db.delete(question)
    await db.commit()
    
    return None
