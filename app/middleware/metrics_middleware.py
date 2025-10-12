from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

from app.api.v1.endpoints.metrics import record_request
from app.core.logging import logger


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP request metrics for Prometheus."""
    
    async def dispatch(self, request: Request, call_next):
        # Record start time
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Extract metrics data
        method = request.method
        endpoint = self._get_endpoint_name(request.url.path)
        status_code = str(response.status_code)
        
        # Record metrics
        try:
            record_request(method, endpoint, status_code, duration)
        except Exception as e:
            logger.error(f"Failed to record metrics: {e}")
        
        return response
    
    def _get_endpoint_name(self, path: str) -> str:
        """
        Convert URL path to a standardized endpoint name for metrics.
        Replaces dynamic segments with placeholders.
        """
        # Remove query parameters
        path = path.split('?')[0]
        
        # Replace common dynamic segments
        import re
        path = re.sub(r'/\d+', '/{id}', path)  # Replace numeric IDs
        path = re.sub(r'/[a-f0-9\-]{8,}', '/{uuid}', path)  # Replace UUIDs
        path = re.sub(r'/[^/]+', '/{param}', path)  # Replace other path parameters
        
        # Clean up multiple parameter placeholders
        path = re.sub(r'/\{param\}(\{param\})+', '/{param}', path)
        
        return path or '/'
