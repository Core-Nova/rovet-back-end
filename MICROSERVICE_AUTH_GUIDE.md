# Microservice Authentication Guide

This guide explains how to use RSA-signed JWT tokens for authentication across microservices.

> **For comprehensive best practices, see [BEST_PRACTICES.md](./BEST_PRACTICES.md)**

## Overview

This authentication service uses **RS256** (RSA with SHA-256) for signing JWT tokens. This approach provides:

- ✅ **Security**: Private key stays in the auth service, public key can be safely shared
- ✅ **Scalability**: Other services can verify tokens without contacting the auth service
- ✅ **Decentralization**: No shared secrets across services
- ✅ **Standard**: RS256 is the industry standard (OAuth 2.0, OpenID Connect)

## Architecture

```
┌─────────────────┐
│  Auth Service   │  Signs tokens with private key
│  (This Repo)    │
└────────┬────────┘
         │ Issues JWT tokens
         │
         ▼
┌─────────────────┐
│   Client App    │  Receives JWT token
└────────┬────────┘
         │ Sends token to microservices
         │
         ▼
┌─────────────────┐      ┌─────────────────┐
│ Microservice A  │      │ Microservice B  │  Verify tokens with public key
│                 │      │                 │  (No need to call auth service)
└─────────────────┘      └─────────────────┘
```

## Setup

### 1. Generate RSA Key Pair

Run the key generation script:

```bash
python scripts/generate_rsa_keys.py
```

This creates:
- `private_key.pem` - Keep this secret! Never commit to version control.
- `public_key.pem` - Safe to share with other microservices

### 2. Configure Environment Variables

Add to your `.env` file:

```env
# JWT Configuration
JWT_ALGORITHM=RS256
JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Important**: 
- Store the private key securely (environment variable, secret manager, etc.)
- The private key should never be committed to version control
- The public key can be shared with other microservices

### 3. Token Payload Structure

JWT tokens include the following claims:

```json
{
  "sub": 123,                    // User ID
  "role": "ADMIN",               // User role (ADMIN, USER)
  "permissions": [               // Role-based permissions
    "users:read",
    "users:write",
    "users:delete",
    "admin:access"
  ],
  "email": "user@example.com",   // User email
  "name": "John Doe",            // User full name (optional)
  "is_active": true,             // User active status
  "iat": 1234567890,            // Issued at timestamp
  "exp": 1234571490             // Expiration timestamp
}
```

### 4. Permissions

Permissions are role-based:

**ADMIN Role:**
- `users:read` - Read all users
- `users:write` - Create/update users
- `users:delete` - Delete users
- `admin:access` - Admin-only endpoints

**USER Role:**
- `users:read:own` - Read own user data
- `profile:read:own` - Read own profile
- `profile:write:own` - Update own profile

## Integration for Other Microservices

### Option 1: Fetch Public Key via API

The auth service provides endpoints to retrieve the public key:

#### Get Public Key (PEM format)

```bash
curl https://auth-service/api/v1/auth/public-key
```

Response:
```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----
```

#### Get Public Key (JWKS format)

```bash
curl https://auth-service/api/v1/auth/jwks
```

Response:
```json
{
  "keys": [
    {
      "kty": "RSA",
      "use": "sig",
      "alg": "RS256",
      "n": "...",
      "e": "AQAB"
    }
  ]
}
```

### Option 2: Use Shared Public Key File

Copy `public_key.pem` to your microservice and load it:

```python
with open("public_key.pem", "r") as f:
    public_key = f.read()
```

### Python Example: Verifying Tokens

```python
from jose import jwt, JWTError
import requests

# Option 1: Fetch public key from auth service
def get_public_key():
    response = requests.get("https://auth-service/api/v1/auth/public-key")
    return response.text

# Option 2: Load from file
def get_public_key():
    with open("public_key.pem", "r") as f:
        return f.read()

# Verify token
def verify_token(token: str) -> dict:
    """
    Verify a JWT token and return the payload.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        JWTError: If token is invalid or expired
    """
    public_key = get_public_key()
    
    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"]
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")

# Usage in FastAPI endpoint
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

def get_current_user(token: str = Depends(security)) -> dict:
    """FastAPI dependency to get current user from JWT token."""
    try:
        payload = verify_token(token.credentials)
        return payload
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

# Check permissions
def require_permission(permission: str):
    """Decorator to require a specific permission."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = kwargs.get('current_user')
            if not user or permission not in user.get('permissions', []):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {permission}"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Example endpoint
@router.get("/protected")
def protected_endpoint(current_user: dict = Depends(get_current_user)):
    # Check if user has required permission
    if "users:read" not in current_user.get("permissions", []):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions"
        )
    
    return {
        "message": "Access granted",
        "user_id": current_user["sub"],
        "role": current_user["role"]
    }
```

### Node.js Example: Verifying Tokens

```javascript
const jwt = require('jsonwebtoken');
const axios = require('axios');

// Fetch public key
async function getPublicKey() {
  const response = await axios.get('https://auth-service/api/v1/auth/public-key');
  return response.data;
}

// Verify token
async function verifyToken(token) {
  const publicKey = await getPublicKey();
  
  try {
    const payload = jwt.verify(token, publicKey, {
      algorithms: ['RS256']
    });
    return payload;
  } catch (error) {
    throw new Error(`Invalid token: ${error.message}`);
  }
}

// Express middleware
const express = require('express');
const app = express();

app.use(async (req, res, next) => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or invalid token' });
  }
  
  const token = authHeader.split(' ')[1];
  
  try {
    const payload = await verifyToken(token);
    req.user = payload;
    next();
  } catch (error) {
    return res.status(401).json({ error: error.message });
  }
});

// Check permissions
function requirePermission(permission) {
  return (req, res, next) => {
    if (!req.user.permissions.includes(permission)) {
      return res.status(403).json({ 
        error: `Missing required permission: ${permission}` 
      });
    }
    next();
  };
}

// Example endpoint
app.get('/protected', requirePermission('users:read'), (req, res) => {
  res.json({
    message: 'Access granted',
    user_id: req.user.sub,
    role: req.user.role
  });
});
```

## Security Best Practices

1. **Private Key Security**
   - Never commit private keys to version control
   - Store in environment variables or secret managers (AWS Secrets Manager, HashiCorp Vault, etc.)
   - Rotate keys periodically

2. **Public Key Distribution**
   - Share public key securely with other microservices
   - Consider using a key management service
   - Cache public keys in microservices (they rarely change)

3. **Token Validation**
   - Always verify token signature
   - Check expiration (`exp` claim)
   - Validate required claims (`sub`, `role`, `permissions`)

4. **HTTPS**
   - Always use HTTPS in production
   - Public key endpoints should be over HTTPS

5. **Token Expiration**
   - Use short-lived tokens (default: 30 minutes)
   - Implement refresh token mechanism for long-lived sessions

## Migration from HS256

If you're currently using HS256 (HMAC with shared secret), you can migrate:

1. Generate RSA key pair
2. Set `JWT_ALGORITHM=RS256` in environment
3. Configure `JWT_PRIVATE_KEY` and `JWT_PUBLIC_KEY`
4. The system will automatically use RS256 for new tokens
5. Old HS256 tokens will continue to work until they expire

## Troubleshooting

### "JWT_PRIVATE_KEY is required for RS256 algorithm"
- Ensure `JWT_PRIVATE_KEY` is set in environment variables
- Check that the key is properly formatted (PEM format)

### "JWT_PUBLIC_KEY is required for RS256 algorithm"
- Ensure `JWT_PUBLIC_KEY` is set in environment variables
- This is needed for token verification

### Token verification fails in microservice
- Verify the public key matches the private key used for signing
- Check that the algorithm is set to "RS256"
- Ensure the token hasn't expired

## Additional Resources

- [JWT.io](https://jwt.io/) - JWT debugger and documentation
- [RFC 7519](https://tools.ietf.org/html/rfc7519) - JSON Web Token specification
- [RFC 7517](https://tools.ietf.org/html/rfc7517) - JSON Web Key (JWK) specification
- [OAuth 2.0](https://oauth.net/2/) - OAuth 2.0 specification

