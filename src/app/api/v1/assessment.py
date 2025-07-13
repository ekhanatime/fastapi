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
    score_points: float
    is_correct: bool
    display_order: int
    
    class Config:
        from_attributes = True

class QuestionSchema(BaseModel):
    id: int
    category_id: str
    question_text: str
    question_type: str
    is_required: bool
    display_order: int
    weight: float
    is_active: bool
    options: List[QuestionOptionSchema] = []
    
    class Config:
        from_attributes = True

class CategorySchema(BaseModel):
    id: str
    title: str
    description: Optional[str]
    icon: Optional[str]
    display_order: int
    is_active: bool
    questions: List[QuestionSchema] = []
    
    class Config:
        from_attributes = True

class AssessmentFullSchema(BaseModel):
    categories: List[CategorySchema]

from ...core.db.database import async_get_db

router = APIRouter(prefix="/assessment-data", tags=["Assessment Data"])

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

    # Map options to questions
    options_by_qid = {}
    for opt in options:
        options_by_qid.setdefault(opt.question_id, []).append(opt)

    # Map questions to categories
    questions_by_cat = {}
    for q in questions:
        q.options = options_by_qid.get(q.id, [])
        questions_by_cat.setdefault(q.category_id, []).append(q)

    # Attach questions to categories
    for c in categories:
        c.questions = questions_by_cat.get(c.id, [])
    logging.info(f"Returning categories with nested questions and options: {categories}")
    return {"categories": categories}
