from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..core.db.database import Base


class QuestionOption(Base):
    __tablename__ = "question_options"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    option_text = Column(Text, nullable=False)
    option_value = Column(String(100), nullable=False)
    score_points = Column(Float, default=0.0)
    is_correct = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    
    # Relationships
    question = relationship("Question", back_populates="options")

    def __repr__(self):
        return f"<QuestionOption(id={self.id}, question_id={self.question_id}, text='{self.option_text[:30]}...')>"
