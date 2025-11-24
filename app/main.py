"""
FastAPI application entry point.

REFACTORED:
- Removed duplicate health check
- Added request validation middleware  
- Proper middleware ordering
- Cleaner structure
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
)
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.docs import get_api_documentation, get_api_summary
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.auth_middleware import AuthMiddleware, AdminMiddleware
from app.middleware.metrics_middleware import MetricsMiddleware
from app.middleware.security_middleware import SecurityMiddleware
from app.middleware.request_validation_middleware import RequestValidationMiddleware
from app.api.v1.api import api_router
from app.api.v1.endpoints.metrics import get_metrics


# Create FastAPI application
app = FastAPI(
    title="Rovet Backend API",
    description=get_api_summary(),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Mount static files if directory exists
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


# ==================== Custom Documentation Routes ====================

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with static assets."""
    return get_swagger_ui_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.PROJECT_NAME} - Swagger UI",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """Custom ReDoc documentation."""
    return get_redoc_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.PROJECT_NAME} - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )


# ==================== Middleware Configuration ====================
# Order matters! Middleware is executed in reverse order of registration
# (Last added = First executed)

# 1. CORS - Allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Security headers - Add security headers to responses
app.add_middleware(SecurityMiddleware)

# 3. Metrics - Collect request metrics
app.add_middleware(MetricsMiddleware)

# 4. Logging - Log requests and responses
app.add_middleware(LoggingMiddleware)

# 5. Request validation - Validate request size and content-type
app.add_middleware(RequestValidationMiddleware)

# 6. Admin authorization - Check admin access for admin routes
app.add_middleware(AdminMiddleware)

# 7. Authentication - Verify JWT tokens
app.add_middleware(AuthMiddleware)


# ==================== Route Registration ====================

# Include API v1 router with prefix
app.include_router(api_router, prefix=settings.API_V1_STR)

# Direct metrics endpoint for Prometheus (without /api/v1 prefix)
@app.get("/api/metrics", include_in_schema=False)
async def metrics_endpoint():
    """
    Direct metrics endpoint for Prometheus scraping.
    
    This bypasses the /api/v1 prefix for easier Prometheus configuration.
    """
    return await get_metrics()


# ==================== Root Health Check ====================

@app.get("/", tags=["Health"])
def root():
    """
    Root endpoint - simple health check.
    
    Returns basic status without database connection check.
    For detailed health check with DB, use /api/v1/health
    """
    return {
        "status": "ok",
        "message": "Rovet Backend API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


# Note: Removed duplicate /health endpoint
# Use /api/v1/health for detailed health check with database


# ==================== OpenAPI Customization ====================

app.openapi = lambda: get_api_documentation(app)
