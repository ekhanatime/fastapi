from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from models.category import Category
from models.question import Question
from models.question_option import QuestionOption
from schemas.assessment import AssessmentFullSchema, CategorySchema, QuestionSchema, QuestionOptionSchema
from core.db.session import get_db

router = APIRouter(prefix="/assessment", tags=["Assessment"])

@router.get("/full", response_model=AssessmentFullSchema)
def get_full_assessment(db: Session = Depends(get_db)):
    # Fetch all categories
    categories = db.query(Category).order_by(Category.display_order).all()
    # Fetch all questions
    questions = db.query(Question).order_by(Question.display_order).all()
    # Fetch all options
    options = db.query(QuestionOption).order_by(QuestionOption.display_order).all()

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

    return {"categories": categories}
