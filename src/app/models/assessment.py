from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.db.database import Base
import uuid
from enum import Enum


class AssessmentStatus(str, Enum):
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_profile_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    
    # Assessment metadata
    status = Column(String(20), default="started")  # Will be enum in production
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Answers and results
    answers = Column(JSON, nullable=True)  # Store all answers as JSON
    total_score = Column(Float, nullable=True)
    max_possible_score = Column(Float, nullable=True)
    percentage_score = Column(Float, nullable=True)
    
    # Category scores (for detailed breakdown)
    category_scores = Column(JSON, nullable=True)  # Store category-wise scores
    
    # Recommendations and insights
    risk_level = Column(String(20), nullable=True)  # low, medium, high, critical
    recommendations = Column(JSON, nullable=True)  # Store recommendations as JSON
    insights = Column(Text, nullable=True)
    
    # Sharing and reporting
    share_token = Column(String(255), nullable=True, unique=True)
    is_shared = Column(Boolean, default=False)
    report_generated = Column(Boolean, default=False)
    report_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    # user_profile = relationship("UserProfile", back_populates="assessments")  # Temporarily disabled
    
    # Indexes
    __table_args__ = (
        Index('idx_assessments_user_profile', 'user_profile_id'),
        Index('idx_assessments_status', 'status'),
        Index('idx_assessments_completed', 'completed_at'),
        Index('idx_assessments_risk_level', 'risk_level'),
        Index('idx_assessments_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<Assessment(id={self.id}, user_profile_id={self.user_profile_id}, status='{self.status}')>"
