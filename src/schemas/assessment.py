from pydantic import BaseModel
from typing import List, Optional, Union
import uuid

class QuestionOptionSchema(BaseModel):
    id: uuid.UUID
    option_value: str
    option_label: str
    is_correct: bool
    display_order: int

    class Config:
        orm_mode = True

class QuestionSchema(BaseModel):
    id: int
    category_id: str
    question_text: str
    question_type: str
    weight: Optional[int]
    scenario: Optional[str]
    display_order: Optional[int]
    options: List[QuestionOptionSchema] = []

    class Config:
        orm_mode = True

class CategorySchema(BaseModel):
    id: str
    title: str
    description: Optional[str]
    icon: Optional[str]
    display_order: Optional[int]
    questions: List[QuestionSchema] = []

    class Config:
        orm_mode = True

class AssessmentFullSchema(BaseModel):
    categories: List[CategorySchema]
