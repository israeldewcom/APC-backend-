# ------------------------------------------------------------------------------
# Stage 1: Base image with common system dependencies
# ------------------------------------------------------------------------------
FROM python:3.12-slim AS base

# Environment variables to optimise Python runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for Python packages and media processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    ffmpeg \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ------------------------------------------------------------------------------
# Stage 2: Dependencies – install Python packages
# ------------------------------------------------------------------------------
FROM base AS dependencies

COPY requirements.txt .

# Install Python packages. Use --no-cache-dir to keep image size small.
RUN pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------------------------
# Stage 3: Production – copy application code and finalise
# ------------------------------------------------------------------------------
FROM dependencies AS production

# Copy the entire project into the container
COPY . .

# Generate static files (must run after code is in place)
RUN python manage.py collectstatic --noinput

# Create directories for logs and media (if not present)
RUN mkdir -p /app/logs /app/media

# Create a non‑root user to run the application
RUN addgroup --system apc && \
    adduser --system --group apc && \
    chown -R apc:apc /app

USER apc

# Health check endpoint (must be implemented in Django)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Expose the port Gunicorn will listen on
EXPOSE 8000

# Command to run the ASGI server
CMD ["gunicorn", "apc_project.asgi:application", \
     "-w", "4", "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", "--timeout", "120", \
     "--access-logfile", "-", "--error-logfile", "-"]
