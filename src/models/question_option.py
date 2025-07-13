from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base
import uuid

Base = declarative_base()

class QuestionOption(Base):
    __tablename__ = 'question_options'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete='CASCADE'))
    option_value = Column(String(100))
    option_label = Column(Text)
    is_correct = Column(Boolean, default=False)
    display_order = Column(Integer)

    question = relationship('Question', back_populates='options')
