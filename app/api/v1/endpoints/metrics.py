from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY,
)
import time

router = APIRouter()

# Define Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Counter(
    'active_connections_total',
    'Total active connections'
)

# Custom metrics for your application
USER_REGISTRATIONS = Counter(
    'user_registrations_total',
    'Total user registrations'
)

LOGIN_ATTEMPTS = Counter(
    'login_attempts_total',
    'Total login attempts',
    ['status']
)

DATABASE_QUERIES = Counter(
    'database_queries_total',
    'Total database queries',
    ['operation', 'table']
)

@router.get("/metrics", response_class=PlainTextResponse)
async def get_metrics():
    """
    Prometheus metrics endpoint.
    Returns application metrics in Prometheus format.
    """
    return generate_latest(REGISTRY)

# Helper functions to update metrics
def record_request(method: str, endpoint: str, status_code: int, duration: float):
    """Record HTTP request metrics."""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

def record_user_registration():
    """Record a user registration."""
    USER_REGISTRATIONS.inc()

def record_login_attempt(status: str):
    """Record a login attempt."""
    LOGIN_ATTEMPTS.labels(status=status).inc()

def record_database_query(operation: str, table: str):
    """Record a database query."""
    DATABASE_QUERIES.labels(operation=operation, table=table).inc()

def record_active_connection():
    """Record an active connection."""
    ACTIVE_CONNECTIONS.inc()
