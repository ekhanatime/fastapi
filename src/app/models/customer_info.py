from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, DateTime, func, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid as uuid_pkg
from ..core.db.database import Base
import enum


class LeadStatusEnum(enum.Enum):
    NEW = "New"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    CUSTOMER = "Customer"


class CustomerInfo(Base):
    __tablename__ = "customer_info"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid_pkg.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    company_name = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    job_title = Column(String(255), nullable=True)
    company_size = Column(String(50), nullable=True)
    industry = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    lead_source = Column(String(100), nullable=True)
    lead_status = Column(Enum(LeadStatusEnum), default=LeadStatusEnum.NEW)
    assigned_to = Column(String(255), nullable=True)
    company_share_token = Column(String(255), unique=True, nullable=True)
    subscription_plan = Column(String(50), default='free')
    max_submissions = Column(Integer, default=1)
    used_submissions = Column(Integer, default=0)
    subscription_expires_at = Column(DateTime(timezone=True), nullable=True)
    payment_status = Column(String(50), default='active')
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships - temporarily disabled to avoid circular dependencies
    # user = relationship("User", back_populates="customer_info")
    
    def __repr__(self):
        return f"<CustomerInfo(id='{self.id}', user_id='{self.user_id}', company_name='{self.company_name}', lead_status='{self.lead_status}')>"
