# ---- Base stage ----
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies (minimal set for the packages we kept)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc g++ libffi-dev libssl-dev \
    libjpeg-dev libpng-dev libwebp-dev \
    ffmpeg curl netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ---- Dependencies stage ----
FROM base AS dependencies

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Production stage ----
FROM dependencies AS production

# Copy the entire project
COPY . .

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs

# --- Dynamic settings discovery ---
# Find the settings.py file and extract its module name.
# This works even if the project is in a subdirectory.
RUN set -e; \
    SETTINGS_PATH=$(find . -name "settings.py" -not -path "*/venv/*" -not -path "*/site-packages/*" | head -n 1); \
    if [ -z "$SETTINGS_PATH" ]; then \
        echo "❌ settings.py not found in the project!"; \
        echo "📁 Current directory contents:"; \
        ls -laR . | head -n 100; \
        exit 1; \
    fi; \
    # Convert path to Python module (e.g., ./apc_project/settings.py -> apc_project.settings)
    MODULE_NAME=$(echo "$SETTINGS_PATH" | sed 's|^\./||' | sed 's|/|.|g' | sed 's|\.py$||'); \
    echo "🔍 Found settings at: $SETTINGS_PATH"; \
    echo "🔧 Setting DJANGO_SETTINGS_MODULE=$MODULE_NAME"; \
    echo "export DJANGO_SETTINGS_MODULE=$MODULE_NAME" >> /tmp/django_env; \
    cat /tmp/django_env >> ~/.bashrc

# Load the environment variable for subsequent RUN commands
SHELL ["/bin/bash", "-c"]
RUN source /tmp/django_env && echo "DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"

# Collect static files
RUN source /tmp/django_env && python manage.py collectstatic --noinput

# Create a non‑root user
RUN addgroup --system apc && \
    adduser --system --group apc && \
    chown -R apc:apc /app

USER apc

# Healthcheck (adjust if your /health/ endpoint exists)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run with gunicorn + uvicorn worker (ASGI)
CMD ["gunicorn", "apc_project.asgi:application", \
     "-w", "4", "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", "--timeout", "120", \
     "--access-logfile", "-", "--error-logfile", "-"]
