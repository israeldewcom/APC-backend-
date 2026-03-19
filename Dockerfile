FROM python:3.12-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y \
    libpq-dev gcc g++ libffi-dev libssl-dev \
    libjpeg-dev libpng-dev libwebp-dev \
    ffmpeg curl netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

FROM base as dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM dependencies as production
COPY . .
RUN python manage.py collectstatic --noinput && \
    mkdir -p /app/logs /app/media

RUN addgroup --system apc && \
    adduser --system --group apc && \
    chown -R apc:apc /app

USER apc

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

CMD ["gunicorn", "apc_project.asgi:application", \
     "-w", "4", "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", "--timeout", "120", \
     "--access-logfile", "-", "--error-logfile", "-"]
