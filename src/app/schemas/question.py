from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_CHOICE = "single_choice"
    TEXT = "text"


class QuestionBase(BaseModel):
    category_id: str = Field(..., max_length=50, description="Category ID")
    question_text: str = Field(..., description="Question text")
    question_type: QuestionType = Field(QuestionType.MULTIPLE_CHOICE, description="Question type")
    is_required: bool = Field(True, description="Whether question is required")
    display_order: int = Field(0, description="Display order")
    weight: float = Field(1.0, description="Question weight for scoring")
    is_active: bool = Field(True, description="Whether question is active")


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    category_id: Optional[str] = Field(None, max_length=50, description="Category ID")
    question_text: Optional[str] = Field(None, description="Question text")
    question_type: Optional[QuestionType] = Field(None, description="Question type")
    is_required: Optional[bool] = Field(None, description="Whether question is required")
    display_order: Optional[int] = Field(None, description="Display order")
    weight: Optional[float] = Field(None, description="Question weight for scoring")
    is_active: Optional[bool] = Field(None, description="Whether question is active")


class QuestionResponse(QuestionBase):
    id: int

    class Config:
        from_attributes = True


class QuestionWithOptions(QuestionResponse):
    options: List["QuestionOptionResponse"] = []


class QuestionList(BaseModel):
    questions: List[QuestionResponse]
    total: int


# Forward reference for QuestionOption
from app.schemas.question_option import QuestionOptionResponse
QuestionWithOptions.model_rebuild()
