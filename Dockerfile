# Stage 1: Build React frontend
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend
COPY endorbit-frontend/package.json endorbit-frontend/package-lock.json ./
RUN npm ci
COPY endorbit-frontend/ ./
RUN npm run build

# Stage 2: Final Python image
FROM python:3.12-slim
WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django backend source
COPY manage.py .
COPY endorbit/ ./endorbit/
COPY aihandler/ ./aihandler/
COPY templates/ ./templates/

# Copy frontend build from builder stage (served by WhiteNoise)
COPY --from=frontend-builder /app/frontend/dist/ ./frontend-dist/

# Copy and set up entrypoint
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
