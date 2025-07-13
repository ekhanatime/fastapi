from pydantic import BaseModel, Field
from typing import Optional


class CategoryBase(BaseModel):
    title: str = Field(..., max_length=255, description="Category title")
    description: Optional[str] = Field(None, description="Category description")
    icon: Optional[str] = Field(None, max_length=100, description="Category icon")
    display_order: int = Field(0, description="Display order")
    is_active: bool = Field(True, description="Whether category is active")


class CategoryCreate(CategoryBase):
    id: str = Field(..., max_length=50, description="Category ID (e.g., 'password_security')")


class CategoryUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255, description="Category title")
    description: Optional[str] = Field(None, description="Category description")
    icon: Optional[str] = Field(None, max_length=100, description="Category icon")
    display_order: Optional[int] = Field(None, description="Display order")
    is_active: Optional[bool] = Field(None, description="Whether category is active")


class CategoryResponse(CategoryBase):
    id: str

    class Config:
        from_attributes = True


class CategoryList(BaseModel):
    categories: list[CategoryResponse]
    total: int
