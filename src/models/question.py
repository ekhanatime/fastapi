from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

class QuestionTypeEnum(enum.Enum):
    single = 'single'
    multiple = 'multiple'

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    category_id = Column(String(50), ForeignKey('categories.id'))
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionTypeEnum))
    weight = Column(Integer)
    scenario = Column(Text)
    display_order = Column(Integer)

    category = relationship('Category')
    options = relationship('QuestionOption', back_populates='question', cascade='all, delete-orphan')
