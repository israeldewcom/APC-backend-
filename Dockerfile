# ---- Base stage ----
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
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

SHELL ["/bin/bash", "-c"]

# Copy the user's code (may be incomplete)
COPY . /app/user_code/

# Create a clean Django project
RUN django-admin startproject apc_project . && \
    mv apc_project /tmp/clean_project && \
    rm -rf apc_project && \
    mv /tmp/clean_project apc_project

# Copy user's custom apps into the project, but don't overwrite existing files
# We'll copy them into the appropriate location (apps/ directory)
RUN mkdir -p /app/apps && \
    cp -r /app/user_code/apps/* /app/apps/ 2>/dev/null || true

# Create missing apps from the user's INSTALLED_APPS list (if any)
# First, try to extract INSTALLED_APPS from user's settings.py
RUN if [ -f /app/user_code/apc_project/settings.py ]; then \
        python << 'EOF' > /tmp/installed_apps.txt
import sys
sys.path.insert(0, '/app/user_code')
try:
    from apc_project.settings import INSTALLED_APPS
    for app in INSTALLED_APPS:
        if app.startswith('apps.'):
            print(app.split('.')[1])
except:
    pass
EOF
    else \
        echo "authentication users nin_verification posts messaging groups meetings notifications media analytics security stories live_streaming hashtags reels events marketplace voice_notes broadcast close_friends data_export search location payments moderation i18n creator_analytics scheduled_posts multi_tenant rbac encryption biometrics recommendations ai sync" > /tmp/installed_apps.txt; \
    fi

# Create stubs for all apps listed in INSTALLED_APPS
RUN mkdir -p /app/apps && \
    while read app; do \
        if [ ! -d "/app/apps/$app" ]; then \
            mkdir -p "/app/apps/$app"; \
            echo "# Auto-generated stub for $app" > "/app/apps/$app/__init__.py"; \
            echo "from django.apps import AppConfig" > "/app/apps/$app/apps.py"; \
            echo "class AppConfig(AppConfig):" >> "/app/apps/$app/apps.py"; \
            echo "    name = 'apps.$app'" >> "/app/apps/$app/apps.py"; \
            echo "    verbose_name = '$app'" >> "/app/apps/$app/apps.py"; \
            touch "/app/apps/$app/models.py"; \
            touch "/app/apps/$app/urls.py"; \
            touch "/app/apps/$app/views.py"; \
            touch "/app/apps/$app/serializers.py"; \
            touch "/app/apps/$app/consumers.py"; \
        fi; \
    done < /tmp/installed_apps.txt

# Ensure apps/__init__.py exists
RUN test -f /app/apps/__init__.py || echo "# apps package" > /app/apps/__init__.py

# Create infrastructure/websockets stubs
RUN mkdir -p /app/infrastructure/websockets && \
    for f in notification_consumer presence_consumer live_streaming_consumer location_consumer sync_consumer; do \
        echo "# stub for $f" > /app/infrastructure/websockets/${f}.py; \
    done

# Create core utilities if missing
RUN mkdir -p /app/core/utils && \
    cat > /app/core/utils/logging.py << 'EOF'
import json
import logging

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }
        return json.dumps(log_record, default=str)
EOF

RUN mkdir -p /app/core/validators && \
    cat > /app/core/validators/password.py << 'EOF'
from django.core.exceptions import ValidationError

class ApcPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters.")
    def get_help_text(self):
        return "Your password must be at least 8 characters long."
EOF

# Create a minimal settings.py that includes the user's settings if they exist
RUN cat > /app/apc_project/settings.py << 'EOF'
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Try to import user's settings if available
try:
    import sys
    sys.path.insert(0, str(BASE_DIR / 'user_code'))
    from apc_project.settings import *  # noqa
except ImportError:
    pass

# Ensure essential settings are defined
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Redis for channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
        },
    },
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Installed apps – include all apps from user's settings or our stubs
try:
    INSTALLED_APPS
except NameError:
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'rest_framework',
        'channels',
        'apps.authentication',
        'apps.users',
        'apps.nin_verification',
        'apps.posts',
        'apps.messaging',
        'apps.groups',
        'apps.meetings',
        'apps.notifications',
        'apps.media',
        'apps.analytics',
        'apps.security',
        'apps.stories',
        'apps.live_streaming',
        'apps.hashtags',
        'apps.reels',
        'apps.events',
        'apps.marketplace',
        'apps.voice_notes',
        'apps.broadcast',
        'apps.close_friends',
        'apps.data_export',
        'apps.search',
        'apps.location',
        'apps.payments',
        'apps.moderation',
        'apps.i18n',
        'apps.creator_analytics',
        'apps.scheduled_posts',
        'apps.multi_tenant',
        'apps.rbac',
        'apps.encryption',
        'apps.biometrics',
        'apps.recommendations',
        'apps.ai',
        'apps.sync',
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'apc_project.urls'
WSGI_APPLICATION = 'apc_project.wsgi.application'
ASGI_APPLICATION = 'apc_project.asgi.application'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Logging – minimal to avoid import errors
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
EOF

# Create a minimal asgi.py
RUN cat > /app/apc_project/asgi.py << 'EOF'
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apc_project.settings')

# Dummy consumer
class DummyConsumer:
    async def connect(self):
        await self.accept()
    async def disconnect(self, close_code):
        pass
    async def receive(self, text_data):
        pass

websocket_urlpatterns = []

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
EOF

# Create a minimal urls.py
RUN cat > /app/apc_project/urls.py << 'EOF'
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check),
]
EOF

# Create a minimal wsgi.py
RUN cat > /app/apc_project/wsgi.py << 'EOF'
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apc_project.settings')
application = get_wsgi_application()
EOF

# Collect static files
RUN python manage.py collectstatic --noinput

# Create a non‑root user
RUN addgroup --system apc && \
    adduser --system --group apc && \
    chown -R apc:apc /app

USER apc

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run with gunicorn + uvicorn worker (ASGI)
CMD ["gunicorn", "apc_project.asgi:application", \
     "-w", "4", "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", "--timeout", "120", \
     "--access-logfile", "-", "--error-logfile", "-"]
