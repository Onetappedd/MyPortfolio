FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install development tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the entire application
COPY . .

# Create Alembic directory if it doesn't exist
RUN mkdir -p /app/alembic/versions

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Command to run on container start will be provided by docker-compose