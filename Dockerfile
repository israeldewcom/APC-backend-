FROM python:3.12-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y \
    libpq-dev gcc g++ libffi-dev libssl-dev \
    libjpeg-dev libpng-dev libwebp-dev \
    ffmpeg curl netcat-traditional \
    # NEW – required for PyAV (aiortc) compilation
    pkg-config \
    libavcodec-dev libavformat-dev libavutil-dev \
    libavdevice-dev libavfilter-dev libswscale-dev libswresample-dev \
    libsrtp2-dev libopus-dev libvpx-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
