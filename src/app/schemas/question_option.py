from pydantic import BaseModel, Field
from typing import Optional


class QuestionOptionBase(BaseModel):
    question_id: int = Field(..., description="Question ID")
    option_text: str = Field(..., description="Option text")
    option_value: str = Field(..., max_length=100, description="Option value")
    score_points: float = Field(0.0, description="Score points for this option")
    is_correct: bool = Field(False, description="Whether this is the correct option")
    display_order: int = Field(0, description="Display order")


class QuestionOptionCreate(QuestionOptionBase):
    pass


class QuestionOptionUpdate(BaseModel):
    question_id: Optional[int] = Field(None, description="Question ID")
    option_text: Optional[str] = Field(None, description="Option text")
    option_value: Optional[str] = Field(None, max_length=100, description="Option value")
    score_points: Optional[float] = Field(None, description="Score points for this option")
    is_correct: Optional[bool] = Field(None, description="Whether this is the correct option")
    display_order: Optional[int] = Field(None, description="Display order")


class QuestionOptionResponse(QuestionOptionBase):
    id: int

    class Config:
        from_attributes = True


class QuestionOptionList(BaseModel):
    options: list[QuestionOptionResponse]
    total: int
