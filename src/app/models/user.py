from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Index
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


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)  # Nullable for leads
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
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    # Note: Assessments are linked via UserProfile, not directly to User
    
    # Indexes
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_company', 'company_name'),
        Index('idx_users_lead_status', 'lead_status'),
        Index('idx_users_subscription', 'subscription_tier'),
        Index('idx_users_created_at', 'created_at'),
    )

    def __init__(self, **kwargs):
        """Initialize User with keyword arguments."""
        super().__init__()
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', lead_status='{self.lead_status}')>"
