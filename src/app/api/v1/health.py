from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime

from ...core.db.database import async_get_db

router = APIRouter(tags=["Health Check"])

# Root health endpoint for requests to /health (without /api/v1 prefix)
@router.get("/", include_in_schema=False)
async def root_health_check():
    """Root health check endpoint accessible at /health"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Security Assessment API",
        "message": "FastAPI backend is operational"
    }

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Security Assessment API"
    }

@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(async_get_db)):
    """Detailed health check with database connectivity"""
    try:
        # Test database connection
        result = await db.execute(text("SELECT 1"))
        db_status = "connected" if result else "error"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Security Assessment API",
        "database": {
            "status": db_status
        },
        "version": "1.0.0"
    }


@router.get("/health/simple")
async def simple_health_check():
    """
    Simple health check for load balancers
    """
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@router.get("/health/database")
async def database_health_check(db: AsyncSession = Depends(async_get_db)):
    """
    Database-specific health check
    """
    try:
        # Test basic connection
        await db.execute(text("SELECT 1"))
        
        # Test table access
        await db.execute(text("SELECT COUNT(*) FROM users LIMIT 1"))
        await db.execute(text("SELECT COUNT(*) FROM categories LIMIT 1"))
        await db.execute(text("SELECT COUNT(*) FROM questions LIMIT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "tables": "accessible",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
