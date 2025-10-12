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
from app.api.v1.api import api_router
from app.api.v1.endpoints.metrics import get_metrics


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

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.PROJECT_NAME} - Swagger UI",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.PROJECT_NAME} - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(MetricsMiddleware)
app.add_middleware(LoggingMiddleware)

app.add_middleware(AdminMiddleware)
app.add_middleware(AuthMiddleware)

app.include_router(api_router, prefix=settings.API_V1_STR)

# Add direct metrics endpoint for Prometheus (without /api/v1 prefix)
@app.get("/api/metrics", include_in_schema=False)
async def metrics_endpoint():
    """Direct metrics endpoint for Prometheus scraping."""
    return await get_metrics()

app.openapi = lambda: get_api_documentation(app)

@app.get("/", tags=["Health Check"])
def health_check():
    """
    Health check endpoint to verify API is running.
    """
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/health", tags=["Health Check"])
def health_check():
    """
    Health check endpoint to verify API is running.
    """
    return {"status": "healthy", "version": "1.0.0"}