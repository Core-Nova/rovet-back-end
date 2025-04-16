import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()

        logger.info(
            "Incoming request",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "client_host": request.client.host if request.client else None,
            }
        )

        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "process_time": f"{process_time:.4f}s"
                }
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "path": request.url.path,
                    "method": request.method,
                    "process_time": f"{process_time:.4f}s",
                    "error": str(e)
                },
                exc_info=True
            )
            raise 