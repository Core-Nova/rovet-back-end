# FastAPI Microservices Authentication - Best Practices Guide

This document outlines the industry best practices implemented in this authentication service for microservices architecture.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [JWT Token Standards](#jwt-token-standards)
3. [FastAPI Dependencies Pattern](#fastapi-dependencies-pattern)
4. [Permission System](#permission-system)
5. [Microservice Integration](#microservice-integration)
6. [Security Best Practices](#security-best-practices)

## Architecture Overview

### Design Principles

1. **Stateless Authentication**: JWTs are stateless, allowing services to verify tokens without shared state
2. **Asymmetric Cryptography**: RS256 (RSA) allows public key distribution without security risk
3. **Token-Based Authorization**: Permissions embedded in tokens eliminate need for database lookups
4. **Dependency Injection**: FastAPI's dependency system provides clean, reusable auth patterns

### Token Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ 1. Login (email, password)
       ▼
┌─────────────────┐
│  Auth Service   │  Generates JWT with RS256
│  (This Repo)    │  - Access Token (30 min)
└──────┬──────────┘  - Refresh Token (7 days)
       │ 2. Returns tokens
       ▼
┌─────────────┐
│   Client    │  Stores tokens securely
└──────┬──────┘
       │ 3. Request with Bearer token
       ▼
┌─────────────────┐      ┌─────────────────┐
│ Microservice A  │      │ Microservice B  │
│                 │      │                 │
│ Verifies token  │      │ Verifies token  │
│ with public key │      │ with public key │
│ (No DB lookup)  │      │ (No DB lookup)  │
└─────────────────┘      └─────────────────┘
```

## JWT Token Standards

### Standard Claims (RFC 7519)

Our implementation follows RFC 7519 (JSON Web Token) standards:

```json
{
  "iss": "rovet-auth-service",     // Issuer - identifies token issuer
  "aud": "rovet-services",         // Audience - intended recipients
  "exp": 1234567890,               // Expiration - token expiry time
  "iat": 1234567890,               // Issued At - when token was created
  "sub": "123",                     // Subject - user ID
  "jti": "unique-token-id",         // JWT ID - unique identifier
  "type": "access"                  // Token type (access/refresh)
}
```

### Custom Claims

```json
{
  "role": "ADMIN",                  // User role
  "permissions": [                  // Granular permissions
    "users:read",
    "users:write",
    "users:delete",
    "admin:access"
  ],
  "email": "user@example.com",     // User email (optional)
  "name": "John Doe",              // User name (optional)
  "is_active": true                // User status (optional)
}
```

### Token Types

1. **Access Token**
   - Short-lived (default: 30 minutes)
   - Contains user permissions
   - Used for API requests

2. **Refresh Token**
   - Long-lived (default: 7 days)
   - Used to obtain new access tokens
   - Does not contain permissions

## FastAPI Dependencies Pattern

### Token Verification (For Microservices)

Use this when you only need to verify the token and check permissions:

```python
from app.api.dependencies.auth import get_token_payload
from app.dto.token import TokenPayload

@router.get("/protected")
def protected_endpoint(payload: TokenPayload = Depends(get_token_payload)):
    """
    This endpoint verifies the token without database lookup.
    Perfect for microservices that don't have user database access.
    """
    user_id = payload.sub
    permissions = payload.permissions
    role = payload.role
    
    return {"user_id": user_id, "permissions": permissions}
```

### User Lookup (For Auth Service)

Use this when you need full user data from database:

```python
from app.api.dependencies.auth import get_current_user
from app.models.user import User

@router.get("/profile")
def get_profile(user: User = Depends(get_current_user)):
    """
    This endpoint verifies token and performs database lookup.
    Use in the authentication service when you need full user data.
    """
    return user
```

### Permission-Based Access Control

```python
from app.api.dependencies.auth import require_permission

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    payload: TokenPayload = Depends(require_permission("users:delete"))
):
    """
    Only users with 'users:delete' permission can access this endpoint.
    """
    # Delete user logic
    return {"message": "User deleted"}
```

### Role-Based Access Control

```python
from app.api.dependencies.auth import require_role
from app.models.user import UserRole

@router.get("/admin/dashboard")
def admin_dashboard(
    payload: TokenPayload = Depends(require_role(UserRole.ADMIN))
):
    """
    Only ADMIN role can access this endpoint.
    """
    return {"dashboard": "data"}
```

### Multiple Permissions (AND)

```python
@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    payload: TokenPayload = Depends(
        require_permission("users:read", "users:write")
    )
):
    """
    User must have BOTH 'users:read' AND 'users:write' permissions.
    """
    # Update user logic
    pass
```

### Any Permission (OR)

```python
from app.api.dependencies.auth import require_any_permission

@router.get("/users")
def list_users(
    payload: TokenPayload = Depends(
        require_any_permission("users:read", "admin:access")
    )
):
    """
    User must have EITHER 'users:read' OR 'admin:access' permission.
    """
    # List users logic
    pass
```

### Convenience Dependencies

```python
from app.api.dependencies.auth import RequireAdmin, RequireUser

@router.get("/admin-only")
def admin_only(payload: TokenPayload = Depends(RequireAdmin)):
    """Only admins can access."""
    pass

@router.get("/user-or-admin")
def user_or_admin(payload: TokenPayload = Depends(RequireUser)):
    """Both users and admins can access."""
    pass
```

## Permission System

### Permission Format

Permissions follow a hierarchical format:

```
resource:action[:scope]
```

Examples:
- `users:read` - Read all users
- `users:read:own` - Read own user data
- `users:write` - Create/update users
- `users:delete` - Delete users
- `admin:access` - Admin-only access

### Role-to-Permission Mapping

**ADMIN Role:**
```python
[
    "users:read",
    "users:write",
    "users:delete",
    "admin:access"
]
```

**USER Role:**
```python
[
    "users:read:own",
    "profile:read:own",
    "profile:write:own"
]
```

### Extending Permissions

To add new permissions, update `_get_permissions_for_role()` in `app/core/security.py`:

```python
def _get_permissions_for_role(role: UserRole) -> list:
    permissions = {
        UserRole.ADMIN: [
            "users:read",
            "users:write",
            "users:delete",
            "admin:access",
            "reports:read",  # New permission
        ],
        UserRole.USER: [
            "users:read:own",
            "profile:read:own",
            "profile:write:own",
        ],
    }
    return permissions.get(role, [])
```

## Microservice Integration

### Step 1: Get Public Key

```python
import requests

# Fetch public key from auth service
response = requests.get("https://auth-service/api/v1/auth/public-key")
public_key = response.text
```

### Step 2: Verify Tokens

```python
from jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

def verify_token(token: str = Depends(security)):
    """Verify JWT token using public key."""
    try:
        payload = jwt.decode(
            token.credentials,
            public_key,
            algorithms=["RS256"],
            audience="rovet-services",  # Must match JWT_AUDIENCE
            issuer="rovet-auth-service"  # Must match JWT_ISSUER
        )
        
        # Validate token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        return payload
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
```

### Step 3: Check Permissions

```python
@router.get("/data")
def get_data(payload: dict = Depends(verify_token)):
    """Check permissions from token payload."""
    permissions = payload.get("permissions", [])
    
    if "data:read" not in permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing required permission: data:read"
        )
    
    return {"data": "..."}
```

### Step 4: Token Propagation

When calling other microservices, propagate the token:

```python
import httpx

async def call_other_service(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://other-service/api/data",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

## Security Best Practices

### 1. Token Storage

**Client-Side:**
- ✅ Use HTTP-only cookies (most secure)
- ✅ Use secure storage (localStorage/sessionStorage) if cookies not possible
- ❌ Never store in plain text
- ❌ Never log tokens

**Server-Side:**
- ✅ Never store tokens in database
- ✅ Validate tokens on every request
- ✅ Check expiration before processing

### 2. Key Management

**Private Key:**
- ✅ Store in environment variables or secret manager
- ✅ Never commit to version control
- ✅ Rotate periodically (every 90 days recommended)
- ✅ Use different keys for dev/staging/production

**Public Key:**
- ✅ Can be shared via API endpoint
- ✅ Can be cached by microservices
- ✅ Update cache when key rotates

### 3. Token Validation

Always validate:
- ✅ Signature (automatic with public key)
- ✅ Expiration (`exp` claim)
- ✅ Issuer (`iss` claim)
- ✅ Audience (`aud` claim)
- ✅ Token type (`type` claim)

### 4. HTTPS

- ✅ Always use HTTPS in production
- ✅ Enforce HTTPS for token endpoints
- ✅ Use secure cookies with `Secure` flag

### 5. Token Expiration

- ✅ Short-lived access tokens (15-30 minutes)
- ✅ Longer-lived refresh tokens (7-30 days)
- ✅ Implement token refresh mechanism
- ✅ Revoke refresh tokens on logout

### 6. Error Handling

```python
from fastapi import HTTPException, status

try:
    payload = verify_token(token)
except jwt.ExpiredSignatureError:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired"
    )
except jwt.InvalidTokenError:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token"
    )
```

### 7. Logging

- ✅ Log authentication failures
- ✅ Log permission denials
- ✅ Never log tokens or passwords
- ✅ Use structured logging

### 8. Rate Limiting

- ✅ Implement rate limiting on login endpoint
- ✅ Implement rate limiting on refresh endpoint
- ✅ Use exponential backoff for failed attempts

## Configuration

### Environment Variables

```env
# JWT Configuration
JWT_ALGORITHM=RS256
JWT_ISSUER=rovet-auth-service
JWT_AUDIENCE=rovet-services
JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"

# Token Expiration
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Generate Keys

```bash
python scripts/generate_rsa_keys.py
```

## Testing

### Unit Tests

```python
def test_token_verification():
    token = create_access_token(subject=1, role=UserRole.ADMIN)
    payload = verify_token(token)
    assert payload["sub"] == "1"
    assert payload["role"] == "ADMIN"
```

### Integration Tests

```python
def test_protected_endpoint(client, token):
    response = client.get(
        "/protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

## References

- [RFC 7519 - JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)
- [RFC 7517 - JSON Web Key (JWK)](https://tools.ietf.org/html/rfc7517)
- [OAuth 2.0 Best Practices](https://oauth.net/2/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io](https://jwt.io/) - JWT debugger and documentation

