from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid


class LeadCaptureRequest(BaseModel):
    email: EmailStr
    interested_in_contact: Optional[bool] = True


class LeadCaptureResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None
    is_existing_user: bool = False
    temporary_password: Optional[str] = None
    requires_password_change: bool = False
    show_login_option: bool = False
