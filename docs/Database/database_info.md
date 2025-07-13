"""
Complete SQLAlchemy models for the cybersecurity assessment system
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from enum import Enum
from datetime import datetime

Base = declarative_base()

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

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

# ===== USER MODELS =====

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    company_size = Column(SQLEnum(CompanySize), nullable=True)
    industry = Column(String(100), nullable=True)
    
    # Subscription info
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    assessments_count = Column(Integer, default=0)
    max_assessments = Column(Integer, default=3)
    
    # Lead tracking
    lead_status = Column(SQLEnum(LeadStatus), default=LeadStatus.NEW)
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
    assessments = relationship("Assessment", back_populates="user")
    company_submissions = relationship("CompanyAssessmentSubmission", back_populates="company_owner")
    
    # Indexes
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_company', 'company_name'),
        Index('idx_users_lead_status', 'lead_status'),
        Index('idx_users_subscription', 'subscription_tier'),
        Index('idx_users_created_at', 'created_at'),
    )

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_super_admin = Column(Boolean, default=False)
    
    # Permissions
    can_manage_users = Column(Boolean, default=True)
    can_manage_assessments = Column(Boolean, default=True)
    can_manage_questions = Column(Boolean, default=False)
    can_view_analytics = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

# ===== ASSESSMENT MODELS =====

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
    category_scores = relationship("CategoryScore", back_populates="category")
    recommendations = relationship("Recommendation", back_populates="category")

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

class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Scores
    overall_score = Column(Integer, nullable=False)  # 0-100
    total_score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    
    # Submission details
    answers = Column(JSONB, nullable=False)  # Store all answers
    interested_in_contact = Column(Boolean, default=True)
    submission_ip = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="assessments")
    category_scores = relationship("CategoryScore", back_populates="assessment", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="assessment", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_assessments_user', 'user_id'),
        Index('idx_assessments_created', 'created_at'),
        Index('idx_assessments_score', 'overall_score'),
        Index('idx_assessments_contact', 'interested_in_contact'),
    )

class CategoryScore(Base):
    __tablename__ = "category_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    category_id = Column(String(50), ForeignKey("categories.id"), nullable=False)
    
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    questions_count = Column(Integer, nullable=False)
    percentage = Column(Integer, nullable=False)  # 0-100
    
    # Relationships
    assessment = relationship("Assessment", back_populates="category_scores")
    category = relationship("Category", back_populates="category_scores")

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    category_id = Column(String(50), ForeignKey("categories.id"), nullable=False)
    
    priority = Column(SQLEnum(Priority), nullable=False)
    recommendation = Column(Text, nullable=False)
    action_items = Column(JSONB, nullable=False)  # List of action items
    
    # Relationships
    assessment = relationship("Assessment", back_populates="recommendations")
    category = relationship("Category", back_populates="recommendations")

# ===== COMPANY SHARING MODELS =====

class CompanyAssessmentSubmission(Base):
    __tablename__ = "company_assessment_submissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    submitter_email = Column(String(255), nullable=False)
    
    # Assessment data (similar to Assessment but for non-registered users)
    overall_score = Column(Integer, nullable=False)
    total_score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    answers = Column(JSONB, nullable=False)
    
    # Submission details
    interested_in_contact = Column(Boolean, default=True)
    submission_ip = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company_owner = relationship("User", back_populates="company_submissions")
    
    # Indexes
    __table_args__ = (
        Index('idx_company_submissions_owner', 'company_owner_id'),
        Index('idx_company_submissions_email', 'submitter_email'),
        Index('idx_company_submissions_created', 'created_at'),
    )

# ===== SYSTEM MODELS =====

class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    setting_key = Column(String(100), unique=True, nullable=False)
    setting_value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("admins.id"), nullable=True)
    
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSONB, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_activity_logs_user', 'user_id'),
        Index('idx_activity_logs_admin', 'admin_id'),
        Index('idx_activity_logs_action', 'action'),
        Index('idx_activity_logs_created', 'created_at'),
    )

# ===== SEARCH OPTIMIZATION =====

class SearchIndex(Base):
    __tablename__ = "search_indexes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_type = Column(String(50), nullable=False)  # 'user', 'assessment', etc.
    resource_id = Column(String(100), nullable=False)
    searchable_text = Column(Text, nullable=False)
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Full-text search index
    __table_args__ = (
        Index('idx_search_type', 'resource_type'),
        Index('idx_search_resource', 'resource_id'),
        # PostgreSQL specific full-text search index
        Index('idx_search_text', 'searchable_text', postgresql_using='gin', postgresql_ops={'searchable_text': 'gin_trgm_ops'}),
    )