# ---- Base stage ----
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies (includes everything needed for aiortc, Pillow, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc g++ libffi-dev libssl-dev \
    libjpeg-dev libpng-dev libwebp-dev \
    ffmpeg curl netcat-traditional \
    # For PyAV (aiortc) – if you keep aiortc
    pkg-config \
    libavcodec-dev libavformat-dev libavutil-dev \
    libavdevice-dev libavfilter-dev libswscale-dev libswresample-dev \
    libsrtp2-dev libopus-dev libvpx-dev \
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

# Create necessary directories (staticfiles and media)
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Collect static files
RUN python manage.py collectstatic --noinput

# Create a non‑root user to run the app
RUN addgroup --system apc && \
    adduser --system --group apc && \
    chown -R apc:apc /app

USER apc

# Healthcheck (optional but recommended)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Use gunicorn with uvicorn worker for ASGI (Channels)
CMD ["gunicorn", "apc_project.asgi:application", \
     "-w", "4", "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", "--timeout", "120", \
     "--access-logfile", "-", "--error-logfile", "-"]
