from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from uuid import UUID


class AssessmentStartRequest(BaseModel):
    user_id: UUID = Field(..., description="User ID from main User table to start assessment for")


class AnswerSubmission(BaseModel):
    question_id: int = Field(..., description="Question ID")
    selected_options: List[int] = Field(..., description="List of selected option IDs")
    text_answer: Optional[str] = Field(None, description="Text answer for open-ended questions")


class AssessmentSubmission(BaseModel):
    assessment_id: UUID = Field(..., description="Assessment ID")
    answers: List[AnswerSubmission] = Field(..., description="List of answers")


class SharedAssessmentSubmission(BaseModel):
    company_token: str = Field(..., description="Company sharing token")
    answers: List[AnswerSubmission] = Field(..., description="List of answers")
    submission_ip: Optional[str] = Field(None, description="IP address of submission")
    user_agent: Optional[str] = Field(None, description="User agent string")
    browser_fingerprint: Optional[str] = Field(None, description="Browser fingerprint for duplicate detection")


class CategoryScore(BaseModel):
    category_id: str
    category_title: str
    score: float
    max_score: float
    percentage: float
    risk_level: str


class AssessmentResult(BaseModel):
    assessment_id: UUID
    user_profile_id: UUID
    status: str
    total_score: float
    max_possible_score: float
    percentage_score: float
    risk_level: str
    category_scores: List[CategoryScore]
    recommendations: List[str]
    insights: Optional[str] = None
    completed_at: datetime
    share_token: Optional[str] = None

    class Config:
        from_attributes = True


class AssessmentResponse(BaseModel):
    id: UUID
    user_profile_id: UUID
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_score: Optional[float] = None
    max_possible_score: Optional[float] = None
    percentage_score: Optional[float] = None
    risk_level: Optional[str] = None
    is_shared: bool
    share_token: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AssessmentList(BaseModel):
    assessments: List[AssessmentResponse]
    total: int


class AssessmentStartResponse(BaseModel):
    assessment_id: UUID
    message: str
    questions_count: int
    estimated_time_minutes: int
