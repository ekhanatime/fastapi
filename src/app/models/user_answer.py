from sqlalchemy import Column, String, Text, Integer, Boolean, DECIMAL, ARRAY, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid as uuid_pkg
from ..core.db.database import Base


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_pkg.uuid4)
    # assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    assessment_id = Column(UUID(as_uuid=True), nullable=False)  # Temporarily removed FK constraint
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_options = Column(ARRAY(Text), nullable=True)  # Array of selected option values
    is_correct = Column(Boolean, nullable=True)
    points_earned = Column(DECIMAL(10, 2), default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships - temporarily disabled to avoid circular dependencies
    # assessment = relationship("Assessment", back_populates="user_answers")
    # question = relationship("Question", back_populates="user_answers")
    
    # Unique constraint
    __table_args__ = (
        {"schema": None},
    )
    
    def __repr__(self):
        return f"<UserAnswer(id='{self.id}', assessment_id='{self.assessment_id}', question_id='{self.question_id}')>"
