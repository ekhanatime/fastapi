from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from ...api.dependencies import get_current_user
from ...core.db.database import async_get_db
from ...core.security import get_password_hash, verify_password
from ...crud.crud_users import crud_users

router = APIRouter(tags=["password"])


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)")


class PasswordChangeResponse(BaseModel):
    success: bool
    message: str


@router.post("/change-password", response_model=PasswordChangeResponse)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)]
):
    """Change user password after verifying current password."""
    try:
        # Get the full user record to access hashed_password
        user = await crud_users.get(db=db, id=current_user["id"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify current password
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Hash new password
        new_hashed_password = get_password_hash(password_data.new_password)
        
        # Update password in database
        await crud_users.update(
            db=db,
            object=user,
            object_data={"hashed_password": new_hashed_password}
        )
        
        return PasswordChangeResponse(
            success=True,
            message="Password changed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to change password: {str(e)}"
        )
