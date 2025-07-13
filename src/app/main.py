from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# from .admin.initialize import create_admin_interface
from .api import router
from .core.config import settings
from .core.setup import create_application, lifespan_factory

# admin = create_admin_interface()  # Disabled to avoid crudadmin dependency
admin = None


@asynccontextmanager
async def lifespan_with_admin(app: FastAPI) -> AsyncGenerator[None, None]:
    """Custom lifespan that includes admin initialization."""
    # Get the default lifespan
    default_lifespan = lifespan_factory(settings)

    # Run the default lifespan initialization and our admin initialization
    async with default_lifespan(app):
        # Initialize admin interface if it exists
        if admin:
            # Initialize admin database and setup
            await admin.initialize()

        yield


app = create_application(router=router, settings=settings, lifespan=lifespan_with_admin)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Customer frontend
        "http://localhost:8080",  # Alternative frontend port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Root health endpoint for direct /health requests (fixes 404 errors)
@app.get("/health")
async def root_health():
    """Root health check endpoint accessible at /health"""
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Security Assessment API",
        "message": "FastAPI backend is operational",
        "endpoints": {
            "docs": "/docs",
            "health_detailed": "/api/v1/health/detailed",
            "assessment": "/api/v1/assessment",
            "admin": "/api/v1/admin"
        }
    }

# API Test Page route
@app.get("/")
async def api_test_page():
    """Serve the API test page as the main entrypoint"""
    static_file = os.path.join(static_dir, "api-test.html")
    if os.path.exists(static_file):
        return FileResponse(static_file)
    return {"message": "API Test Page not found", "docs": "/docs"}

# Mount admin interface if enabled
if admin:
    app.mount(settings.CRUD_ADMIN_MOUNT_PATH, admin.app)
