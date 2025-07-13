from sqlalchemy import Column, String, ForeignKey, DateTime, func, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid as uuid_pkg
from ..core.db.database import Base
import enum


class EmailStatusEnum(enum.Enum):
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"


class EmailNotification(Base):
    __tablename__ = "email_notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_pkg.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    email_type = Column(String(50), nullable=True)
    recipient_email = Column(String(255), nullable=True)
    subject = Column(String(500), nullable=True)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    email_status = Column(Enum(EmailStatusEnum), nullable=True)
    external_message_id = Column(String(255), nullable=True)
    
    # Relationships - temporarily disabled to avoid circular dependencies
    # assessment = relationship("Assessment", back_populates="email_notifications")
    
    def __repr__(self):
        return f"<EmailNotification(id='{self.id}', assessment_id='{self.assessment_id}', email_type='{self.email_type}', status='{self.email_status}')>"
