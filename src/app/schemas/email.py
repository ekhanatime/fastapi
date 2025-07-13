from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginCredentials(BaseModel):
    email: EmailStr
    password: str


class SendLoginLinkRequest(BaseModel):
    email: EmailStr
    assessment_id: Optional[str] = None
    login_credentials: LoginCredentials


class SendLoginLinkResponse(BaseModel):
    success: bool
    message: str
    login_link: Optional[str] = None
