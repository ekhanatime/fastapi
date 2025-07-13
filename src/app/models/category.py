from sqlalchemy import Column, String, Text, Integer, Boolean
from sqlalchemy.orm import relationship
from ..core.db.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(String(50), primary_key=True)  # e.g., 'password_security'
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    questions = relationship("Question", back_populates="category")
    # category_scores = relationship("CategoryScore", back_populates="category")  # Temporarily disabled
    # recommendations = relationship("Recommendation", back_populates="category")  # Temporarily disabled

    def __repr__(self):
        return f"<Category(id='{self.id}', title='{self.title}')>"
