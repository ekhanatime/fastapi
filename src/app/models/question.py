from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from ..core.db.database import Base


class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(String(50), ForeignKey("categories.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), default="multiple_choice")  # multiple_choice, single_choice, text
    is_required = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    weight = Column(Float, default=1.0)  # For scoring
    is_active = Column(Boolean, default=True)
    
    # Relationships
    category = relationship("Category", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_questions_category', 'category_id'),
        Index('idx_questions_active', 'is_active'),
    )

    def __repr__(self):
        return f"<Question(id={self.id}, category_id='{self.category_id}', text='{self.question_text[:50]}...')>"
