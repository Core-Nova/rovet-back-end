# Deployment Guide

## Overview

This guide covers secure deployment of the Rovet Backend API to Google Cloud Platform using Cloud Run with Neon DB.

## Security Setup

### 1. GitHub Secrets Configuration

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following secrets:

#### Required Secrets:
- **`DATABASE_URL`**: Your Neon DB connection string
  ```
  postgresql://username:password@host:port/database?sslmode=require
  ```
- **`SECRET_KEY`**: A strong secret key for JWT tokens
  ```
  your-very-secure-secret-key-here
  ```
- **`GCP_SA_KEY`**: Your Google Cloud Service Account key (JSON format)

### 2. Google Cloud Setup

#### Create Service Account:
```bash
gcloud iam service-accounts create rovet-deploy \
  --display-name="Rovet Deployment Service Account"

gcloud projects add-iam-policy-binding core-nova \
  --member="serviceAccount:rovet-deploy@core-nova.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding core-nova \
  --member="serviceAccount:rovet-deploy@core-nova.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding core-nova \
  --member="serviceAccount:rovet-deploy@core-nova.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud iam service-accounts keys create rovet-deploy-key.json \
  --iam-account=rovet-deploy@core-nova.iam.gserviceaccount.com
```

#### Upload Service Account Key to GitHub:
1. Copy the contents of `rovet-deploy-key.json`
2. Go to GitHub repository → Settings → Secrets → Actions
3. Create new secret named `GCP_SA_KEY`
4. Paste the JSON content as the value

### 3. Neon DB Setup

#### Get Connection String:
1. Go to your Neon dashboard
2. Navigate to your project
3. Go to Connection Details
4. Copy the connection string
5. Add it as `DATABASE_URL` secret in GitHub

#### Connection String Format:
```
postgresql://username:password@host:port/database?sslmode=require&channel_binding=require
```

## Deployment Process

### Automatic Deployment
The application automatically deploys when you push to the `main` branch.

### Manual Deployment
```bash
# Build and push image
docker build -t gcr.io/core-nova/rovet-back-end .
docker push gcr.io/core-nova/rovet-back-end

# Deploy to Cloud Run
gcloud run deploy rovet-back-end \
  --image gcr.io/core-nova/rovet-back-end \
  --region europe-west3 \
  --allow-unauthenticated \
  --port 8080 \
  --timeout 300 \
  --memory 1Gi \
  --set-env-vars DATABASE_URL=$DATABASE_URL,ENVIRONMENT=production,SECRET_KEY=$SECRET_KEY
```

## Environment Configuration

### Local Development
The application automatically detects development environment and uses local PostgreSQL.

### Production
The application automatically detects production environment when `DATABASE_URL` is provided.

## Monitoring

### Health Checks
- **Health Endpoint**: `https://your-service-url.run.app/`
- **Metrics**: `https://your-service-url.run.app/api/metrics`
- **API Docs**: `https://your-service-url.run.app/api/docs`

### Logs
```bash
gcloud run logs tail rovet-back-end --region=europe-west3
```

## Troubleshooting

### Common Issues

1. **Migration Failures**
   - Check Cloud Run job execution logs
   - Verify DATABASE_URL is correct
   - Ensure database is accessible from GCP

2. **Authentication Issues**
   - Verify SECRET_KEY is set
   - Check JWT token expiration settings

3. **Database Connection Issues**
   - Verify Neon DB allows connections from GCP IP ranges
   - Check SSL requirements are met

### Debug Commands
```bash
# Check service status
gcloud run services describe rovet-back-end --region=europe-west3

# View recent logs
gcloud run logs read rovet-back-end --region=europe-west3 --limit=50

# Test database connection
gcloud run jobs execute migrate-db --region=europe-west3 --wait
```

## Security Best Practices

1. **Never commit secrets to Git**
2. **Use GitHub Secrets for sensitive data**
3. **Rotate secrets regularly**
4. **Use least-privilege IAM roles**
5. **Enable audit logging**
6. **Use HTTPS for all connections**
7. **Regular security updates**

## Support

For deployment issues:
1. Check GitHub Actions logs
2. Review Cloud Run service logs
3. Verify all secrets are correctly set
4. Ensure database connectivity
