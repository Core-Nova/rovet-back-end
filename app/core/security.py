from datetime import datetime, timedelta
from typing import Any, Union, Optional, Dict, List
from jose import jwt
from passlib.context import CryptContext
import secrets
from app.core.config import settings
from app.models.user import UserRole
from app.core.logging import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _get_signing_key() -> str:
    """Get the appropriate signing key based on algorithm."""
    if settings.JWT_ALGORITHM == "RS256":
        if not settings.JWT_PRIVATE_KEY:
            raise ValueError("JWT_PRIVATE_KEY is required for RS256 algorithm")
        return settings.JWT_PRIVATE_KEY
    else:
        # Fallback to HS256 with SECRET_KEY
        return settings.SECRET_KEY


def _get_verification_key() -> str:
    """Get the appropriate verification key based on algorithm."""
    if settings.JWT_ALGORITHM == "RS256":
        if not settings.JWT_PUBLIC_KEY:
            raise ValueError("JWT_PUBLIC_KEY is required for RS256 algorithm")
        return settings.JWT_PUBLIC_KEY
    else:
        # Fallback to HS256 with SECRET_KEY
        return settings.SECRET_KEY


def create_access_token(
    subject: Union[str, Any],
    role: UserRole,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
    token_type: str = "access"
) -> str:
    """
    Create a JWT access token following industry best practices.
    
    Implements standard JWT claims (RFC 7519):
    - iss (issuer): Identifies the principal that issued the JWT
    - aud (audience): Identifies the recipients that the JWT is intended for
    - exp (expiration): Time after which the JWT expires
    - iat (issued at): Time at which the JWT was issued
    - sub (subject): Identifies the subject of the JWT (user ID)
    - jti (JWT ID): Unique identifier for the JWT
    
    Custom claims:
    - role: User role (ADMIN, USER, etc.)
    - permissions: List of permissions based on role
    - type: Token type (access, refresh)
    
    Args:
        subject: User ID or identifier
        role: User role (ADMIN, USER, etc.)
        expires_delta: Optional custom expiration time
        additional_claims: Optional additional claims to include in token
        token_type: Type of token (access or refresh)
    
    Returns:
        Encoded JWT token string
    """
    now = datetime.utcnow()
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Standard JWT claims (RFC 7519)
    to_encode = {
        "iss": settings.JWT_ISSUER,  # Issuer
        "aud": settings.JWT_AUDIENCE,  # Audience
        "exp": int(expire.timestamp()),  # Expiration
        "iat": int(now.timestamp()),  # Issued at
        "sub": str(subject),  # Subject (user ID)
        "jti": secrets.token_urlsafe(32),  # JWT ID (unique identifier)
        "type": token_type,  # Token type
    }
    
    # Custom claims for authorization
    to_encode.update({
        "role": role.value,
        "permissions": _get_permissions_for_role(role),
    })
    
    # Add any additional claims (email, name, etc.)
    if additional_claims:
        to_encode.update(additional_claims)
    
    signing_key = _get_signing_key()
    encoded_jwt = jwt.encode(
        to_encode,
        signing_key,
        algorithm=settings.JWT_ALGORITHM
    )
    
    logger.debug(f"Created {token_type} JWT token with algorithm {settings.JWT_ALGORITHM}")
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token for obtaining new access tokens.
    
    Refresh tokens are longer-lived and used to obtain new access tokens
    without requiring user re-authentication.
    
    Args:
        subject: User ID or identifier
        expires_delta: Optional custom expiration time (default: 7 days)
    
    Returns:
        Encoded JWT refresh token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    now = datetime.utcnow()
    
    to_encode = {
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "sub": str(subject),
        "jti": secrets.token_urlsafe(32),
        "type": "refresh",
    }
    
    signing_key = _get_signing_key()
    encoded_jwt = jwt.encode(
        to_encode,
        signing_key,
        algorithm=settings.JWT_ALGORITHM
    )
    
    logger.debug(f"Created refresh JWT token")
    return encoded_jwt


def _get_permissions_for_role(role: UserRole) -> list:
    """
    Get permissions list for a given role.
    
    This can be extended to support more granular permissions.
    For now, we use role-based permissions.
    """
    permissions = {
        UserRole.ADMIN: [
            "users:read",
            "users:write",
            "users:delete",
            "admin:access",
        ],
        UserRole.USER: [
            "users:read:own",
            "profile:read:own",
            "profile:write:own",
        ],
    }
    return permissions.get(role, [])


def verify_token(
    token: str,
    audience: Optional[str] = None,
    issuer: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verify and decode a JWT token following industry best practices.
    
    Validates:
    - Token signature
    - Expiration (exp claim)
    - Issuer (iss claim) - if provided
    - Audience (aud claim) - if provided
    
    Args:
        token: JWT token string to verify
        audience: Expected audience (default: settings.JWT_AUDIENCE)
        issuer: Expected issuer (default: settings.JWT_ISSUER)
    
    Returns:
        Decoded token payload
    
    Raises:
        JWTError: If token is invalid, expired, or cannot be verified
    """
    from jose import JWTError
    
    verification_key = _get_verification_key()
    options = {
        "verify_signature": True,
        "verify_exp": True,
        "verify_iss": issuer is not None,
        "verify_aud": audience is not None,
    }
    
    try:
        payload = jwt.decode(
            token,
            verification_key,
            algorithms=[settings.JWT_ALGORITHM],
            audience=audience or settings.JWT_AUDIENCE,
            issuer=issuer or settings.JWT_ISSUER,
            options=options
        )
        return payload
    except JWTError as e:
        logger.error(f"JWT verification failed: {str(e)}")
        raise


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password) 