from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Annotated

from ...models.category import Category
from ...models.question import Question
from ...models.question_option import QuestionOption
# Import schemas for the full assessment data endpoint
from pydantic import BaseModel
from typing import List, Optional

# Define schemas for the full assessment endpoint
class QuestionOptionSchema(BaseModel):
    id: int
    option_text: str
    option_value: str
    score_points: Optional[float] = 0.0
    is_correct: bool
    display_order: int
    
    class Config:
        from_attributes = True

class QuestionSchema(BaseModel):
    id: int
    category_id: str
    question_text: str
    question_type: str
    is_required: Optional[bool] = True
    display_order: int
    weight: Optional[float] = 1.0
    is_active: Optional[bool] = True
    options: List[QuestionOptionSchema] = []
    
    class Config:
        from_attributes = True

class CategorySchema(BaseModel):
    id: str
    title: str
    description: Optional[str]
    icon: Optional[str]
    display_order: int
    is_active: Optional[bool] = True
    questions: List[QuestionSchema] = []
    
    class Config:
        from_attributes = True

class AssessmentFullSchema(BaseModel):
    categories: List[CategorySchema]

from ...core.db.database import async_get_db

router = APIRouter(prefix="/assessment/data", tags=["Assessment Data"])

import logging
logging.basicConfig(level=logging.INFO)

@router.get("/full", response_model=AssessmentFullSchema)
async def get_full_assessment(db: Annotated[AsyncSession, Depends(async_get_db)]):
    # Fetch all categories
    categories_result = await db.execute(select(Category).order_by(Category.display_order))
    categories = categories_result.scalars().all()
    logging.info(f"Fetched categories: {len(categories)}")
    
    # Fetch all questions
    questions_result = await db.execute(select(Question).order_by(Question.display_order))
    questions = questions_result.scalars().all()
    logging.info(f"Fetched questions: {len(questions)}")
    
    # Fetch all options
    options_result = await db.execute(select(QuestionOption).order_by(QuestionOption.display_order))
    options = options_result.scalars().all()
    logging.info(f"Fetched options: {len(options)}")

    # Build response data structure manually to avoid SQLAlchemy lazy loading issues
    options_by_qid = {}
    for opt in options:
        option_data = QuestionOptionSchema(
            id=opt.id,
            option_text=opt.option_text,
            option_value=opt.option_value,
            score_points=opt.score_points if opt.score_points is not None else 0.0,
            is_correct=opt.is_correct,
            display_order=opt.display_order
        )
        options_by_qid.setdefault(opt.question_id, []).append(option_data)

    # Build questions with their options
    questions_by_cat = {}
    for q in questions:
        # Handle None values before passing to schema
        is_required_value = True if q.is_required is None else q.is_required
        is_active_value = True if q.is_active is None else q.is_active
        
        question_data = QuestionSchema(
            id=q.id,
            category_id=q.category_id,
            question_text=q.question_text,
            question_type=q.question_type,
            is_required=is_required_value,
            is_active=is_active_value,
            weight=q.weight if q.weight is not None else 1.0,
            display_order=q.display_order,
            options=options_by_qid.get(q.id, [])
        )
        questions_by_cat.setdefault(q.category_id, []).append(question_data)

    # Build categories with their questions
    category_data_list = []
    for c in categories:
        # Handle None values before passing to schema
        is_active_value = True if c.is_active is None else c.is_active
        
        category_data = CategorySchema(
            id=c.id,
            title=c.title,
            description=c.description,
            icon=c.icon,
            display_order=c.display_order,
            is_active=is_active_value,
            questions=questions_by_cat.get(c.id, [])
        )
        category_data_list.append(category_data)
    
    logging.info(f"Returning {len(category_data_list)} categories with nested questions and options")
    return {"categories": category_data_list}
