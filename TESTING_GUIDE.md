# Testing Guide - Running Commands in Docker

This guide provides step-by-step instructions for testing the API using Docker commands as documented in the README.

## Prerequisites

1. Docker and Docker Compose installed
2. Containers running: `docker-compose up -d`

## Step 1: Start Docker Containers

```bash
# Start all services
docker-compose up -d

# Check container status
docker ps

# View logs if needed
docker-compose logs -f api
```

## Step 2: Initialize Database

```bash
# Enter the backend container
docker exec -it rovet-backend sh

# Inside the container, run migrations
alembic upgrade head

# Seed the database with initial users
python -m app.scripts.seed_db

# Exit the container
exit
```

Or run directly without entering the container:

```bash
# Run migrations
docker exec rovet-backend alembic upgrade head

# Seed database
docker exec rovet-backend python -m app.scripts.seed_db
```

## Step 3: Run Tests

```bash
# Run all tests
docker exec rovet-backend pytest app/tests/ -v

# Run specific test file
docker exec rovet-backend pytest app/tests/api/v1/test_auth.py -v

# Run with coverage
docker exec rovet-backend pytest app/tests/ --cov=app --cov-report=html
```

## Step 4: Test API Endpoints

### 4.1 Health Check

```bash
curl http://localhost:8001/
```

Expected response:
```json
{"status": "healthy", "database": "healthy", "version": "1.0.0"}
```

### 4.2 Login (Get Access Token)

```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@rovet.io", "password": "admin123"}'
```

Expected response:
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Save the access_token for subsequent requests!**

### 4.3 Get All Users

```bash
# Replace YOUR_TOKEN with the access_token from login
curl http://localhost:8001/api/v1/users/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected response:
```json
{
  "items": [...],
  "total": 8,
  "page": 1,
  "size": 10,
  "pages": 1
}
```

### 4.4 Get User by ID

```bash
curl http://localhost:8001/api/v1/users/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected response:
```json
{
  "id": 1,
  "email": "admin@rovet.io",
  "full_name": "Admin",
  "role": "ADMIN",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### 4.5 Filter Users

```bash
# Get active users
curl "http://localhost:8001/api/v1/users/?is_active=true" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Search by email
curl "http://localhost:8001/api/v1/users/?email=kamen" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by role
curl "http://localhost:8001/api/v1/users/?role=USER" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4.6 Pagination

```bash
# Get page 1 with 5 items per page
curl "http://localhost:8001/api/v1/users/?page=1&size=5" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get page 2
curl "http://localhost:8001/api/v1/users/?page=2&size=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4.7 Refresh Token

```bash
# Replace REFRESH_TOKEN with the refresh_token from login
curl -X POST http://localhost:8001/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "REFRESH_TOKEN"}'
```

### 4.8 Get Public Key (For Microservices)

```bash
curl http://localhost:8001/api/v1/auth/public-key
```

Expected response:
```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----
```

### 4.9 Get JWKS (JSON Web Key Set)

```bash
curl http://localhost:8001/api/v1/auth/jwks
```

Expected response:
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

## Step 5: Test with Different Users

### Login as Regular User

```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "kamen@rovet.io", "password": "user123"}'
```

### Test Permission-Based Access

Regular users should get 403 Forbidden when trying to access admin endpoints:

```bash
# This should fail for regular users
curl http://localhost:8001/api/v1/users/ \
  -H "Authorization: Bearer USER_TOKEN"
```

## Step 6: Complete Test Script

You can also run the automated test script:

```bash
# Make script executable
docker exec rovet-backend chmod +x /app/scripts/test_api.sh

# Run the script
docker exec rovet-backend /app/scripts/test_api.sh
```

## Troubleshooting

### Container Not Running

```bash
# Check container status
docker ps -a

# Start containers
docker-compose up -d

# View logs
docker-compose logs api
```

### Database Connection Issues

```bash
# Check database container
docker ps | grep rovet-db

# Check database logs
docker-compose logs db

# Test database connection
docker exec rovet-backend python -c "from app.db.session import SessionLocal; db = SessionLocal(); print('Connected!'); db.close()"
```

### Migration Issues

```bash
# Check current migration
docker exec rovet-backend alembic current

# Run migrations
docker exec rovet-backend alembic upgrade head

# Create new migration if needed
docker exec rovet-backend alembic revision --autogenerate -m "description"
```

### Token Issues

If you get 401 Unauthorized:

1. Check that the token is valid (not expired)
2. Verify the token format: `Bearer YOUR_TOKEN`
3. Check that JWT keys are configured:
   ```bash
   docker exec rovet-backend python -c "from app.core.config import settings; print('Algorithm:', settings.JWT_ALGORITHM)"
   ```

## Default Users

After seeding, these users are available:

### Admin
- Email: `admin@rovet.io`
- Password: `admin123`
- Role: ADMIN

### Regular Users (all password: `user123`)
- `kamen@rovet.io`
- `tsetso@rovet.io`
- `nick.bacon@rovet.io`
- `luci@rovet.io`
- `rado@rovet.io`
- `mario@rovet.io`
- `eva@rovet.io`

## API Documentation

Once the service is running, visit:
- Swagger UI: http://localhost:8001/api/docs
- ReDoc: http://localhost:8001/api/redoc
- OpenAPI JSON: http://localhost:8001/api/openapi.json

## Next Steps

1. Review the [BEST_PRACTICES.md](./BEST_PRACTICES.md) for implementation details
2. Check [MICROSERVICE_AUTH_GUIDE.md](./MICROSERVICE_AUTH_GUIDE.md) for microservice integration
3. Read the main [README.md](./README.md) for setup instructions

