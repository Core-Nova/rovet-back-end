# Database Configuration Setup

## Overview

This setup provides a hybrid database configuration:
- **Development (Local)**: Uses your existing local PostgreSQL database
- **Production (GCP)**: Uses Neon DB (serverless PostgreSQL)

## Changes Made

### 1. Updated `app/core/config.py`
- Added `DATABASE_URL` environment variable for production
- Added `ENVIRONMENT` detection
- Modified `assemble_db_connection` to use `DATABASE_URL` when available (production) or build from individual components (development)

### 2. Updated `app/db/session.py`
- Enhanced connection handling for both environments
- Added SSL configuration for Neon DB (production)
- Optimized connection pool settings for serverless (smaller pool, no overflow)
- Added environment-specific logging

### 3. Updated `.github/workflows/deploy.yml`
- Simplified environment variables to use `DATABASE_URL` instead of individual DB components
- Updated migration job to use the same configuration

## Setup Instructions

### 1. GitHub Secrets Configuration

Add this secret to your GitHub repository:

**`DATABASE_URL`**: 
```
postgresql://neondb_owner:npg_dCiVFY50pxrH@ep-winter-dew-agdetep6-pooler.c-2.eu-central-1.aws.neon.tech/rovet_db?sslmode=require&channel_binding=require
```

**Other required secrets:**
- `SECRET_KEY`: Your application secret key
- `GCP_SA_KEY`: Your Google Cloud Service Account key

### 2. Local Development

Your local setup remains unchanged. The application will:
- Use your existing `.env` file or Docker Compose database
- Connect to `db:5432` (your local PostgreSQL)
- Work exactly as before

### 3. Production Deployment

When deployed to GCP Cloud Run, the application will:
- Use the `DATABASE_URL` environment variable
- Connect to Neon DB with SSL
- Use optimized connection settings for serverless

## Environment Detection

The application automatically detects the environment:
- **Development**: When `DATABASE_URL` is not set
- **Production**: When `DATABASE_URL` is provided

## Connection Improvements

The Neon connection string has been enhanced with:
- `sslmode=require`: Ensures secure connections
- `channel_binding=require`: Additional security layer
- Optimized connection pool settings for serverless environments

## Testing

### Local Testing
```bash
# Start your local environment (unchanged)
docker-compose up

# The app will connect to your local PostgreSQL
```

### Production Testing
1. Deploy to GCP with the new configuration
2. Check Cloud Run logs for successful database connection
3. Test your API endpoints

## Troubleshooting

### Common Issues

1. **SSL Connection Errors**: Make sure your Neon DB allows connections from GCP IP ranges
2. **Connection Timeouts**: The configuration includes retry logic and optimized timeouts
3. **Pool Exhaustion**: Serverless-optimized pool settings prevent this

### Logs to Check

Look for these log messages:
- `"Using production database URL: ..."` (production)
- `"Building database URI for development: ..."` (development)
- `"Successfully connected to production database"` (production)
- `"Successfully connected to development database"` (development)

## Migration

Your existing migrations will work with both databases. The migration job in GitHub Actions will run against your Neon DB in production.

## Security Notes

- The Neon connection string contains credentials and should only be stored in GitHub Secrets
- SSL is enforced for production connections
- Connection pooling is optimized for serverless environments
- No database credentials are logged in production (masked in logs)
