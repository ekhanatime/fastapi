from sqlalchemy import Column, String, Text, ForeignKey, DateTime, func, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid as uuid_pkg
from ..core.db.database import Base
import enum


class PriorityEnum(enum.Enum):
    KRITISK = "Kritisk"
    HOY = "Høy"
    MIDDELS = "Middels"
    LAV = "Lav"


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_pkg.uuid4)
    # assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    assessment_id = Column(UUID(as_uuid=True), nullable=False)  # Temporarily removed FK constraint
    category_id = Column(String(50), ForeignKey("categories.id"), nullable=False)
    priority = Column(Enum(PriorityEnum), nullable=True)
    recommendation = Column(Text, nullable=True)
    action_items = Column(ARRAY(Text), nullable=True)  # Array of action items
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships - temporarily disabled to avoid circular dependencies
    # assessment = relationship("Assessment", back_populates="recommendations")
    # category = relationship("Category", back_populates="recommendations")
    
    def __repr__(self):
        return f"<Recommendation(id='{self.id}', assessment_id='{self.assessment_id}', category_id='{self.category_id}', priority='{self.priority}')>"
