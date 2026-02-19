# Multi-stage build for Autonomous Agent Pro

# Stage 1: Build frontend
FROM node:22-alpine AS frontend-builder

WORKDIR /app

# Copy frontend files
COPY client/package.json client/pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install

COPY client/ .
RUN pnpm build

# Stage 2: Build backend and runtime
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY server/ ./server/

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/dist ./client/dist

# Create necessary directories
RUN mkdir -p logs uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production
ENV DEBUG=False

# Expose ports
EXPOSE 8000 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
