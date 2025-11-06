# Rovet Backend API

A FastAPI-based backend service providing user management and authentication functionality.

## Features

* **Authentication** - Secure JWT-based authentication system
* **User Management** - Complete user CRUD operations with role-based access control
* **Admin Controls** - Protected endpoints for user administration
* **Middleware Security** - Token validation and role-based access control
* **Pagination & Filtering** - Advanced user listing with filtering capabilities
* **Prometheus Metrics** - Built-in metrics endpoint for monitoring and observability
* **Hybrid Database Support** - Local PostgreSQL for development, Neon DB for production
* **Cloud Run Ready** - Optimized for Google Cloud Platform deployment

## System Requirements

### Required Software
- Python 3.9 or higher
- Docker Desktop
- Git
- A terminal (Command Prompt/PowerShell for Windows, Terminal for macOS/Linux)

### Hardware Requirements
- At least 4GB RAM
- 10GB free disk space
- Any modern CPU (2015 or newer)

## Installation Guide

### 1. Installing Python

#### Windows
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify installation:
```bash
python --version
```

#### macOS
1. Using Homebrew (recommended):
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.9
```
2. Verify installation:
```bash
python3 --version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.9 python3.9-venv python3-pip
```

### 2. Installing Docker

#### Windows
1. Download [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. Install WSL 2 if prompted (required for Windows 10/11)
3. Restart your computer
4. Start Docker Desktop
5. Verify installation:
```bash
docker --version
docker-compose --version
```

#### macOS
1. Download [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
2. Install the application
3. Start Docker Desktop
4. Verify installation:
```bash
docker --version
docker-compose --version
```

#### Linux (Ubuntu/Debian)
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose

# Add your user to the docker group
sudo usermod -aG docker $USER

# Verify installation (you may need to log out and back in first)
docker --version
docker-compose --version
```

### 3. Installing Git and Setting Up SSH

#### Windows
1. Download [Git for Windows](https://git-scm.com/download/win)
2. Run the installer (use default settings)
3. Generate SSH key:
```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
```
4. Add SSH key to ssh-agent:
```bash
eval $(ssh-agent -s)
ssh-add ~/.ssh/id_ed25519
```
5. Copy the public key:
```bash
clip < ~/.ssh/id_ed25519.pub
```

#### macOS
```bash
# Using Homebrew
brew install git

# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add SSH key to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy the public key
pbcopy < ~/.ssh/id_ed25519.pub
```

#### Linux (Ubuntu/Debian)
```bash
# Install Git
sudo apt install git

# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add SSH key to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy the public key (install xclip if needed)
sudo apt install xclip
xclip -sel clip < ~/.ssh/id_ed25519.pub
```

After generating and copying your SSH key:
1. Go to GitHub > Settings > SSH and GPG keys
2. Click "New SSH key"
3. Paste your copied public key
4. Click "Add SSH key"

## Project Setup

### 1. Clone the Repository
```bash
git clone git@github.com:Core-Nova/rovet-back-end.git
cd rovet-back-end
```

### 2. Environment Setup

Create a `.env` file in the project root:
```bash
# Database (Local Development)
POSTGRES_SERVER=db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=app_db
POSTGRES_PORT=5432

# Application
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8001"]

# Environment (automatically detected)
ENVIRONMENT=development
```

**Note**: For production deployment, the application automatically uses Neon DB when `DATABASE_URL` is provided via environment variables.

### 3. Start Docker Services
```bash
# Build and start containers
docker-compose up -d

# Check container status
docker ps
```

### 4. Initialize Database
```bash
# Enter the backend container
docker exec -it rovet-backend sh

# Run database migrations
alembic upgrade head

# Seed the database with initial users
python -m app.scripts.seed_db
```

### 5. Verify Installation
Visit these URLs in your browser:
- API Documentation: http://localhost:8001/api/docs
- Health Check: http://localhost:8001/
- Metrics Endpoint: http://localhost:8001/api/metrics (Prometheus format)

## Default Users

After seeding the database, the following users will be available:

### Admin User
- Email: admin@rovet.io
- Password: admin123

### Regular Users
All regular users have the password: user123
- kamen@rovet.io
- tsetso@rovet.io
- nick.bacon@rovet.io
- luci@rovet.io
- rado@rovet.io
- mario@rovet.io
- eva@rovet.io

## API Usage

### Authentication

To authenticate, make a POST request to the login endpoint:
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@rovet.io", "password": "admin123"}'
```

Use the returned token in subsequent requests:
```bash
curl -H "Authorization: Bearer {your_token}" http://localhost:8001/api/v1/users
```

### User Management

The API supports the following operations:
- List users (with filtering and pagination)
- Get user by ID
- Create new user
- Update user
- Delete user

#### Filtering Examples

Get active users:
```bash
curl http://localhost:8001/api/v1/users?is_active=true \
  -H "Authorization: Bearer {your_token}"
```

Search users by email:
```bash
curl http://localhost:8001/api/v1/users?email=kamen \
  -H "Authorization: Bearer {your_token}"
```

#### Pagination

All list endpoints support pagination:
```bash
curl http://localhost:8001/api/v1/users?page=2&size=20 \
  -H "Authorization: Bearer {your_token}"
```

## Development

### Running Tests

Inside the Docker container:
```bash
pytest
```

### Run locally without Docker (venv + pip) and use Docker DB

If you prefer to run the API locally without Docker but still use the PostgreSQL database from Docker:

1. Start only the database with Docker:
```bash
docker-compose up -d db
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv .venv
# Windows
. .venv\\Scripts\\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

3. Configure environment variables to point to the Docker DB (host port 5433):
```bash
# Windows PowerShell
$env:POSTGRES_SERVER = "localhost"
$env:POSTGRES_PORT = "5433"
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_PASSWORD = "postgres"
$env:POSTGRES_DB = "app_db"
$env:SECRET_KEY = "your-secret-key-here"

# macOS/Linux
export POSTGRES_SERVER=localhost
export POSTGRES_PORT=5433
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_DB=app_db
export SECRET_KEY=your-secret-key-here
```

4. Run database migrations (optional if you already ran them via Docker):
```bash
alembic upgrade head
```

5. Start the API locally:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

You can now access:
- API Docs: http://localhost:8001/api/docs
- Health: http://localhost:8001/
- Metrics: http://localhost:8001/api/metrics

### Monitoring & Metrics

The application includes built-in Prometheus metrics at `/api/metrics`:
- HTTP request metrics (count, duration)
- Authentication metrics (login attempts, registrations)
- Database query metrics
- Custom application metrics

Access metrics in Prometheus format:
```bash
curl http://localhost:8001/api/metrics
```

### Common Docker Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Rebuild and start services
docker-compose up -d --build

# Remove all containers and volumes (WARNING: This will delete all data)
docker-compose down -v
```

### Troubleshooting

#### Docker Issues
1. **Container not starting**
   ```bash
   # Check logs
   docker-compose logs
   
   # Verify ports are not in use
   netstat -an | grep 8001  # Linux/macOS
   netstat -an | findstr 8001  # Windows
   ```

2. **Database connection issues**
   ```bash
   # Verify database is running
   docker-compose ps
   
   # Check database logs
   docker-compose logs db
   ```

#### Permission Issues
1. **Linux/macOS**:
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

2. **Windows**:
   - Run Docker Desktop as administrator
   - Ensure WSL 2 is properly installed

### Code Structure

```
app/
├── api/            # API routes and endpoints
├── core/           # Core functionality and config
├── db/             # Database models and session
├── middleware/     # Custom middleware
├── models/         # Pydantic models and schemas
├── repositories/   # Database operations
├── scripts/        # Utility scripts
├── services/       # Business logic
└── tests/          # Test suite
```

## Security

- All endpoints (except login and register) require JWT authentication
- Admin endpoints are protected with role-based access control
- Passwords are hashed using bcrypt
- CORS is configured for specified origins only

## Deployment

### Local Development
The application automatically uses your local PostgreSQL database when running with Docker Compose.

### Production (Google Cloud Platform)
The application is configured for deployment to Google Cloud Run with the following features:
- Automatic database migration on startup
- Optimized for serverless environments
- Built-in health checks and metrics
- SSL-enabled database connections (Neon DB)

#### Required GitHub Secrets for Production:
- `DATABASE_URL`: Your Neon DB connection string
- `SECRET_KEY`: Application secret key
- `GCP_SA_KEY`: Google Cloud Service Account key

See `DEPLOYMENT_GUIDE.md` for detailed deployment instructions.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Issues and Solutions

1. **Empty Response from Protected Endpoints**
   - Issue: Getting an empty response when accessing protected endpoints
   - Solution: Make sure to include the trailing slash in the URL
   ```bash
   # Wrong
   curl -X GET "http://localhost:8001/api/v1/users"
   
   # Correct
   curl -X GET "http://localhost:8001/api/v1/users/"
   ```

2. **Authentication Issues**
   - Issue: Getting "Incorrect email or password" error
   - Solution: Use the correct admin credentials from the seed script
   ```bash
   # Correct credentials
   curl -X POST "http://localhost:8001/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@example.com", "password": "admin123"}'
   ```

3. **Database Connection Issues**
   - Issue: Services fail to start due to database connection
   - Solution: Make sure the database service is healthy before starting the API
   ```bash
   # Check database health
   docker-compose ps db
   
   # Restart services if needed
   docker-compose down -v && docker-compose up -d
   ```

4. **Migration Issues**
   - Issue: Database migrations fail during startup
   - Solution: Check the logs for specific errors
   ```bash
   docker-compose logs api
   ```

### Debug Steps

1. **Check Service Status**
   ```bash
   docker-compose ps
   ```

2. **View Service Logs**
   ```bash
   # View all logs
   docker-compose logs
   
   # View specific service logs
   docker-compose logs api
   docker-compose logs db
   ```

3. **Verify Database Connection**
   ```bash
   # Connect to database container
   docker-compose exec db psql -U postgres -d app_db
   
   # List tables
   \dt
   
   # Check users table
   SELECT * FROM users;
   ```

4. **Test API Endpoints**
   ```bash
   # Health check
   curl http://localhost:8001/
   
   # Get admin token
   curl -X POST "http://localhost:8001/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@example.com", "password": "admin123"}'
   
   # Get all users (with token)
   curl -X GET "http://localhost:8001/api/v1/users/" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

5. **Common HTTP Status Codes**
   - 200: Success
   - 307: Temporary Redirect (add trailing slash)
   - 401: Unauthorized (invalid or missing token)
   - 403: Forbidden (insufficient permissions)
   - 404: Not Found (invalid endpoint)
   - 500: Internal Server Error (check logs) 