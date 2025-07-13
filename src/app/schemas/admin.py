from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime


class PaginatedResponse(BaseModel):
    """Generic paginated response schema"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class CustomerDetailResponse(BaseModel):
    """Customer detail response schema"""
    id: str
    email: str
    created_at: datetime
    updated_at: Optional[datetime]
    customer_info: Optional[Dict[str, Any]]
    total_assessments: int
    avg_score: float
    assessments: List[Dict[str, Any]]


class AdminAuthRequest(BaseModel):
    """Admin authentication request"""
    username: str
    password: str


class AdminAuthResponse(BaseModel):
    """Admin authentication response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class SystemSettingsResponse(BaseModel):
    """System settings response"""
    email_notifications_enabled: bool
    max_assessments_per_user: int
    assessment_timeout_minutes: int
    company_share_token_expiry_days: int
    max_company_submissions: int
    maintenance_mode: bool
    registration_enabled: bool
    anonymous_submissions_enabled: bool
    admin_interface_enabled: bool
    redis_enabled: bool
    session_timeout_minutes: int
    max_sessions_per_user: int
    track_events: bool
    track_sessions_in_db: bool


class SystemSettingsUpdate(BaseModel):
    """System settings update request"""
    email_notifications_enabled: Optional[bool] = None
    max_assessments_per_user: Optional[int] = None
    assessment_timeout_minutes: Optional[int] = None
    company_share_token_expiry_days: Optional[int] = None
    max_company_submissions: Optional[int] = None
    maintenance_mode: Optional[bool] = None
    registration_enabled: Optional[bool] = None
    anonymous_submissions_enabled: Optional[bool] = None


class AnalyticsResponse(BaseModel):
    """Analytics response schema"""
    period: str
    start_date: str
    end_date: str
    summary: Dict[str, Any]
    score_distribution: Dict[str, int]
    lead_status_distribution: Dict[str, int]
    daily_trends: List[Dict[str, Any]]


class SystemStatsResponse(BaseModel):
    """System statistics response"""
    total_users: int
    total_assessments: int
    recent_users_24h: int
    recent_assessments_24h: int
    average_score: float
    last_updated: str


class AuditLogEntry(BaseModel):
    """Audit log entry schema"""
    id: str
    timestamp: datetime
    action: str
    user_email: str
    ip_address: str
    user_agent: str
    details: Dict[str, Any]


class AuditLogSummary(BaseModel):
    """Audit log summary schema"""
    period_days: int
    start_date: str
    end_date: str
    summary: Dict[str, int]
