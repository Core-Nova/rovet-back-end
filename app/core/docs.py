from fastapi.openapi.utils import get_openapi

def get_api_documentation(app):
    """
    Generate the OpenAPI documentation for the API.
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Rovet Backend API",
        description="""
        # Rovet Backend API Documentation

        This API provides a comprehensive set of endpoints for user management and authentication.
        
        ## Features
        
        * **Authentication** - Secure JWT-based authentication system
        * **User Management** - Complete user CRUD operations with role-based access control
        * **Admin Controls** - Protected endpoints for user administration
        * **Middleware Security** - Token validation and role-based access control
        * **Pagination & Filtering** - Advanced user listing with filtering capabilities
        
        ## Setup Instructions

        ### 1. Docker Environment
        All commands should be run inside the Docker container. To execute any command:
        ```bash
        # Enter the container shell
        docker exec -it rovet-backend sh

        # Inside the container, you can run commands like:
        python -m app.scripts.seed_db
        pytest
        ```

        ### 2. Database Seeding
        The application comes with pre-configured users for testing:
        ```bash
        # Inside the Docker container
        python -m app.scripts.seed_db
        ```

        This will create the following users:
        - Admin: admin@rovet.io (Password: admin123)
        - Regular Users (Password: user123 for all):
          - kamen@rovet.io
          - tsetso@rovet.io
          - nick.bacon@rovet.io
          - luci@rovet.io
          - rado@rovet.io
          - mario@rovet.io
          - eva@rovet.io
        
        ## Authentication
        
        All protected endpoints require a valid JWT token in the Authorization header:
        ```
        Authorization: Bearer {token}
        ```

        To get a token, use the login endpoint:
        ```bash
        curl -X POST http://localhost:8001/api/v1/auth/login \\
          -H "Content-Type: application/json" \\
          -d '{"email": "admin@rovet.io", "password": "admin123"}'
        ```
        
        ## Admin Access
        
        Endpoints marked with 'Admin only' require admin role access. Regular users will receive a 403 Forbidden response.
        Only the admin@rovet.io user has admin privileges by default.

        ## User Management Features

        ### Filtering Users
        The /users endpoint supports the following filters:
        - email (string): Filter by email address
        - role (string): Filter by role (admin/user)
        - is_active (boolean): Filter by active status

        ### Pagination
        All list endpoints support pagination with:
        - page (int): Page number (default: 1)
        - size (int): Items per page (default: 10)

        Example:
        ```bash
        # Get active users, page 2, 20 items per page
        curl http://localhost:8001/api/v1/users?is_active=true&page=2&size=20 \\
          -H "Authorization: Bearer {your_token}"
        ```
        """,
        version="1.0.0",
        routes=app.routes,
    )
    
    return openapi_schema


def get_api_summary():
    """
    Get a brief summary of the API for the FastAPI app description.
    """
    return """
    # Rovet Backend API

    Comprehensive user management and authentication system with Docker support.
    
    ## Quick Start
    1. Run all commands inside Docker container
    2. Seed database with test users
    3. Use admin@rovet.io/admin123 for admin access
    
    For complete documentation, visit the /api/redoc endpoint.
    """ 