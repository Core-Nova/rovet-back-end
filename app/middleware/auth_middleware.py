from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.auth_service import AuthService
from app.models.user import UserRole
from app.db.session import SessionLocal
from app.core.logging import logger
from app.exceptions.base import UnauthorizedException


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Auth middleware processing request: {request.url.path}")
        
        public_paths = [
            "/",  # Root path
            f"{settings.API_V1_STR}/auth/login",
            f"{settings.API_V1_STR}/auth/register",
            f"{settings.API_V1_STR}/health",
            "/docs",
            "/redoc",
            f"{settings.API_V1_STR}/openapi.json",
            "/static",
        ]

        if request.url.path in public_paths or request.url.path.startswith("/static/"):
            logger.info(f"Request path {request.url.path} is public, skipping auth")
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        logger.info(f"Authorization header: {auth_header}")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.error("Missing or invalid Authorization header")
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid authentication token"}
            )

        token = auth_header.split(" ")[1]
        logger.info(f"Received token: {token}")
        
        logger.info("Attempting to create database session")
        db: Session = SessionLocal()
        try:
            logger.info("Creating AuthService instance")
            auth_service = AuthService(db)
            
            logger.info("Attempting to get current user from token")
            user = auth_service.get_current_user(token)
            logger.info(f"Successfully authenticated user: {user.email} with role {user.role}")
            
            logger.info("Adding user to request state")
            request.state.user = user
            request.state.is_admin = user.role == UserRole.ADMIN
            logger.info(f"User admin status: {request.state.is_admin}")
            
            logger.info("Proceeding to next middleware/handler")
            response = await call_next(request)
            return response
            
        except UnauthorizedException as e:
            logger.error(f"Unauthorized: {str(e.detail)}")
            return JSONResponse(
                status_code=401,
                content={"detail": str(e.detail)}
            )
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication failed"}
            )
        finally:
            logger.info("Closing database session")
            db.close()


class AdminMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Admin middleware processing request: {request.url.path}")
        
        admin_base_path = f"{settings.API_V1_STR}/users"
        
        if not request.url.path.startswith(admin_base_path):
            logger.info(f"Request path {request.url.path} is not an admin route, skipping admin check")
            return await call_next(request)

        if not hasattr(request.state, "user"):
            logger.error("No user found in request state")
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid authentication token"}
            )

        if not request.state.is_admin:
            logger.error(f"User {request.state.user.email} is not an admin")
            return JSONResponse(
                status_code=403,
                content={"detail": "Admin access required"}
            )

        logger.info(f"Admin check passed for user {request.state.user.email}")
        return await call_next(request) 