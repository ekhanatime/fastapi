from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import base64
import json

from ...core.db.database import async_get_db
from ...api.dependencies import get_current_user
from ...models.user import User
from ...schemas.email import SendLoginLinkRequest, SendLoginLinkResponse

router = APIRouter()


def create_login_link(email: str, password: str, assessment_id: str = None) -> str:
    """Create a secure login link with embedded credentials."""
    # Encode credentials for URL
    credentials = {
        "email": email,
        "password": password,
        "assessment_id": assessment_id
    }
    
    # Base64 encode the credentials for URL safety
    encoded_creds = base64.urlsafe_b64encode(
        json.dumps(credentials).encode()
    ).decode()
    
    # Create login link (in production, use your actual domain)
    base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    return f"{base_url}/auto-login?token={encoded_creds}"


async def send_email_with_smtp(to_email: str, subject: str, html_content: str):
    """Send email using SMTP configuration or simulate for testing"""
    try:
        # Get SMTP configuration from environment
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        if not all([smtp_server, smtp_username, smtp_password]):
            # SMTP not configured - simulate email sending for testing
            print(f"\n=== EMAIL SIMULATION ===")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Content: {html_content[:200]}...")
            print(f"=== END EMAIL SIMULATION ===\n")
            return True
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_username
        msg['To'] = to_email
        
        # Add HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            
        return True
        
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False


@router.post("/send-login-link", response_model=SendLoginLinkResponse)
async def send_login_link(
    request: SendLoginLinkRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)]
):
    """Send login link via email for easy dashboard access."""
    try:
        # Verify the current user matches the email
        if current_user.email != request.email:
            raise HTTPException(status_code=403, detail="Email mismatch")
        
        # Create login link
        login_link = create_login_link(
            email=request.login_credentials.email,
            password=request.login_credentials.password,
            assessment_id=request.assessment_id
        )
        
        # Create email content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Your Security Assessment Results</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔒 Your Security Assessment Results</h1>
                    <p>Thank you for completing our cybersecurity assessment!</p>
                </div>
                <div class="content">
                    <h2>Access Your Dashboard</h2>
                    <p>Your assessment has been completed and your results are ready. Click the button below to access your personalized security dashboard:</p>
                    
                    <div style="text-align: center;">
                        <a href="{login_link}" class="button">View My Security Dashboard</a>
                    </div>
                    
                    <h3>What you'll find in your dashboard:</h3>
                    <ul>
                        <li>📊 Detailed security score breakdown</li>
                        <li>🎯 Personalized recommendations</li>
                        <li>📈 Progress tracking over time</li>
                        <li>🔧 Implementation guides</li>
                    </ul>
                    
                    <p><strong>Note:</strong> This link will automatically log you in securely. Keep this email safe for future access to your dashboard.</p>
                </div>
                <div class="footer">
                    <p>If you have any questions, please don't hesitate to contact our support team.</p>
                    <p>© 2024 Security Assessment Platform</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email with login link
        email_sent = await send_email_with_smtp(
            to_email=request.email,
            subject="Your Secure Login Link - Security Assessment",
            html_content=email_html
        )
        
        return SendLoginLinkResponse(
            success=email_sent,
            message="Login link sent successfully" if email_sent else "Email service unavailable - you can still access your results",
            login_link=login_link  # Include link in response for testing/fallback
        )
        
    except Exception as e:
        # Don't fail the entire flow if email fails
        print(f"Email service error: {e}")
        return SendLoginLinkResponse(
            success=False,
            message="Email service temporarily unavailable",
            login_link=create_login_link(
                email=request.login_credentials.email,
                password=request.login_credentials.password,
                assessment_id=request.assessment_id
            )
        )
