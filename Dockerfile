FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy Poetry files
COPY pyproject.toml poetry.lock* ./

# Configure Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --with dev

# Copy application code
COPY . .

# Install the project
RUN poetry install --no-interaction --no-ansi --with dev

# Make startup script executable
RUN chmod +x scripts/start.sh

# Expose port
EXPOSE 8001

# Command to run the application
CMD ["./scripts/start.sh"] 