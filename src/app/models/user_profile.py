from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.db.database import Base
import uuid
from enum import Enum


class SubscriptionTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"


class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CUSTOMER = "customer"


class CompanySize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class UserProfile(Base):
    """
    Extended user profile for assessment-specific data.
    Links to the main User model via user_id foreign key.
    """
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)  # Links to existing User model
    
    # Company and contact information
    full_name = Column(String(255), nullable=True)
    company_name = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    company_size = Column(String(20), nullable=True)  # Will be enum in production
    industry = Column(String(100), nullable=True)
    
    # Subscription info
    subscription_tier = Column(String(20), default="free")  # Will be enum in production
    assessments_count = Column(Integer, default=0)
    max_assessments = Column(Integer, default=3)
    
    # Lead tracking
    lead_status = Column(String(20), default="new")  # Will be enum in production
    lead_source = Column(String(100), nullable=True)
    lead_notes = Column(Text, nullable=True)
    
    # Company sharing
    company_share_token = Column(String(255), nullable=True, unique=True)
    company_share_enabled = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="profile")  # Links to existing User model
    # assessments = relationship("Assessment", back_populates="user_profile")  # Temporarily disabled
    
    # Indexes
    __table_args__ = (
        Index('idx_user_profiles_user_id', 'user_id'),
        Index('idx_user_profiles_company', 'company_name'),
        Index('idx_user_profiles_lead_status', 'lead_status'),
        Index('idx_user_profiles_subscription', 'subscription_tier'),
        Index('idx_user_profiles_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, company='{self.company_name}')>"
