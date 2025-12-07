from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from app.core.config import settings
from app.core.logging import logger

router = APIRouter()


@router.get("/public-key", response_class=PlainTextResponse)
def get_public_key():
    """
    Get the public RSA key for JWT token verification.
    
    This endpoint allows other microservices to retrieve the public key
    needed to verify JWT tokens issued by this authentication service.
    
    The public key is safe to share and can be used by any service that
    needs to verify tokens without contacting this service.
    
    Returns:
        PEM-formatted public key
    
    Example usage in another microservice:
        ```python
        import requests
        public_key = requests.get("https://auth-service/api/v1/auth/public-key").text
        
        from jose import jwt
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        ```
    """
    if settings.JWT_ALGORITHM != "RS256":
        raise HTTPException(
            status_code=501,
            detail="Public key endpoint only available when using RS256 algorithm"
        )
    
    if not settings.JWT_PUBLIC_KEY:
        logger.error("JWT_PUBLIC_KEY not configured")
        raise HTTPException(
            status_code=500,
            detail="Public key not configured"
        )
    
    logger.info("Public key requested by microservice")
    return settings.JWT_PUBLIC_KEY


@router.get("/jwks")
def get_jwks():
    """
    Get JSON Web Key Set (JWKS) for JWT token verification.
    
    This endpoint provides the public key in JWKS format, which is
    the standard format for OAuth 2.0 and OpenID Connect.
    
    Returns:
        JSON Web Key Set containing the public key
    """
    if settings.JWT_ALGORITHM != "RS256":
        raise HTTPException(
            status_code=501,
            detail="JWKS endpoint only available when using RS256 algorithm"
        )
    
    if not settings.JWT_PUBLIC_KEY:
        logger.error("JWT_PUBLIC_KEY not configured")
        raise HTTPException(
            status_code=500,
            detail="Public key not configured"
        )
    
    # Parse the public key to extract key information
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    import base64
    
    try:
        public_key = serialization.load_pem_public_key(
            settings.JWT_PUBLIC_KEY.encode(),
            backend=default_backend()
        )
        
        # Get the public key numbers
        public_numbers = public_key.public_numbers()
        
        # Convert to base64url format (RFC 7517)
        def int_to_base64url(value: int) -> str:
            """Convert integer to base64url-encoded string."""
            byte_length = (value.bit_length() + 7) // 8
            bytes_value = value.to_bytes(byte_length, 'big')
            return base64.urlsafe_b64encode(bytes_value).decode('utf-8').rstrip('=')
        
        # Create JWKS
        jwks = {
            "keys": [
                {
                    "kty": "RSA",
                    "use": "sig",
                    "alg": "RS256",
                    "n": int_to_base64url(public_numbers.n),  # Modulus
                    "e": int_to_base64url(public_numbers.e),   # Exponent
                }
            ]
        }
        
        logger.info("JWKS requested by microservice")
        return jwks
    except Exception as e:
        logger.error(f"Error generating JWKS: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating JWKS: {str(e)}"
        )

