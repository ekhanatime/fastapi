from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Annotated

from ...core.db.database import async_get_db
from ...models.category import Category
from ...schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryList

router = APIRouter()


@router.get("/")
async def list_categories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(async_get_db)
):
    """List all categories with pagination."""
    result = await db.execute(select(Category).offset(skip).limit(limit))
    categories = result.scalars().all()
    count_result = await db.execute(select(Category))
    total = len(count_result.scalars().all())
    
    return CategoryList(
        categories=[CategoryResponse.from_orm(cat) for cat in categories],
        total=total
    )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str, db: AsyncSession = Depends(async_get_db)):
    """Get a specific category by ID."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return CategoryResponse.from_orm(category)


@router.post("/", response_model=CategoryResponse, status_code=201)
async def create_category(category_data: CategoryCreate, db: AsyncSession = Depends(async_get_db)):
    """Create a new category."""
    # Check if category with same id already exists
    result = await db.execute(select(Category).where(Category.id == category_data.id))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this ID already exists")
    
    category = Category(**category_data.dict())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    
    return CategoryResponse.from_orm(category)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str, 
    category_data: CategoryUpdate, 
    db: AsyncSession = Depends(async_get_db)
):
    """Update an existing category."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check for title conflicts if title is being updated
    if category_data.title and category_data.title != category.title:
        result = await db.execute(select(Category).where(Category.title == category_data.title))
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail="Category with this title already exists")
    
    # Update only provided fields
    update_data = category_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    return CategoryResponse.from_orm(category)


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: str, db: AsyncSession = Depends(async_get_db)):
    """Delete a category."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    await db.delete(category)
    await db.commit()
    
    return None
