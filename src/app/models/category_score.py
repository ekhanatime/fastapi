from sqlalchemy import Column, String, Integer, DECIMAL, ForeignKey, DateTime, func, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid as uuid_pkg
from ..core.db.database import Base


class CategoryScore(Base):
    __tablename__ = "category_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_pkg.uuid4)
    # assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    assessment_id = Column(UUID(as_uuid=True), nullable=False)  # Temporarily removed FK constraint
    category_id = Column(String(50), ForeignKey("categories.id"), nullable=False)
    score = Column(DECIMAL(10, 2), nullable=True)
    max_score = Column(DECIMAL(10, 2), nullable=True)
    questions_count = Column(Integer, nullable=True)
    # percentage is calculated as GENERATED column in PostgreSQL: ROUND((score / NULLIF(max_score, 0)) * 100)
    percentage = Column(Integer, nullable=True)  # Will be computed by database
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships - temporarily disabled to avoid circular dependencies
    # assessment = relationship("Assessment", back_populates="category_scores")
    # category = relationship("Category", back_populates="category_scores")
    
    # Unique constraint
    __table_args__ = (
        {"schema": None},
    )
    
    def __repr__(self):
        return f"<CategoryScore(id='{self.id}', assessment_id='{self.assessment_id}', category_id='{self.category_id}', score={self.score})>"
