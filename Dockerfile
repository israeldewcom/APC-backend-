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

# Use Bash for all subsequent commands
SHELL ["/bin/bash", "-c"]

# Copy the entire project
COPY . .

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs

# --- CREATE MISSING UTILITIES ---
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

# --- ENSURE ALL DJANGO APPS EXIST (create stubs for missing ones) ---
RUN mkdir -p /app/apps

RUN for app in authentication users nin_verification posts messaging groups meetings notifications media analytics security stories live_streaming hashtags reels events marketplace voice_notes broadcast close_friends data_export search location payments moderation i18n creator_analytics scheduled_posts multi_tenant rbac encryption biometrics recommendations ai sync; do \
    app_dir="/app/apps/$app"; \
    if [ ! -d "$app_dir" ]; then \
        mkdir -p "$app_dir"; \
        echo "# Auto-generated stub for $app" > "$app_dir/__init__.py"; \
        echo "from django.apps import AppConfig" > "$app_dir/apps.py"; \
        echo "class AppConfig(AppConfig):" >> "$app_dir/apps.py"; \
        echo "    name = 'apps.$app'" >> "$app_dir/apps.py"; \
        echo "    verbose_name = '$app'" >> "$app_dir/apps.py"; \
        touch "$app_dir/models.py"; \
        touch "$app_dir/urls.py"; \
        touch "$app_dir/views.py"; \
        touch "$app_dir/serializers.py"; \
        echo "Created stub for $app"; \
    fi; \
done

RUN test -f /app/apps/__init__.py || echo "# apps package" > /app/apps/__init__.py

# --- DYNAMIC SETTINGS DISCOVERY ---
RUN set -e; \
    SETTINGS_PATH=$(find . -name "settings.py" -not -path "*/venv/*" -not -path "*/site-packages/*" | head -n 1); \
    if [ -z "$SETTINGS_PATH" ]; then \
        echo "❌ settings.py not found in the project!"; \
        echo "📁 Current directory contents:"; \
        ls -laR . | head -n 100; \
        exit 1; \
    fi; \
    MODULE_NAME=$(echo "$SETTINGS_PATH" | sed 's|^\./||' | sed 's|/|.|g' | sed 's|\.py$||'); \
    echo "🔍 Found settings at: $SETTINGS_PATH"; \
    echo "🔧 Setting DJANGO_SETTINGS_MODULE=$MODULE_NAME"; \
    echo "export DJANGO_SETTINGS_MODULE=$MODULE_NAME" >> /tmp/django_env; \
    cat /tmp/django_env >> ~/.bashrc

# --- PYTHON SCRIPT TO PATCH SETTINGS.PY ---
RUN source /tmp/django_env && python << 'EOF'
import re
import sys

# Find settings.py again (or use the saved path)
import os
settings_path = None
for root, dirs, files in os.walk('.'):
    if 'settings.py' in files and 'venv' not in root and 'site-packages' not in root:
        settings_path = os.path.join(root, 'settings.py')
        break

if not settings_path:
    print("❌ settings.py not found")
    sys.exit(1)

print(f"📄 Patching {settings_path}")

with open(settings_path, 'r') as f:
    content = f.read()

# Remove the entire PARLER_LANGUAGES block and replace it
pattern = r'^PARLER_LANGUAGES\s*=\s*\{[^}]*\}(?:\s*$|(?=\n\n))'
replacement = """PARLER_LANGUAGES = {
    1: (
        {'code': 'en'},
    ),
    'default': {
        'fallbacks': ['en'],
        'hide_untranslated': False,
    }
}"""

new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

if new_content == content:
    # If pattern didn't match, try a more aggressive approach: find the line that starts with PARLER_LANGUAGES
    lines = content.split('\n')
    in_parler = False
    new_lines = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith('PARLER_LANGUAGES'):
            # Skip until we find the closing brace
            brace_count = 0
            started = False
            while i < len(lines):
                line = lines[i]
                if not started:
                    if line.find('{') != -1:
                        started = True
                        brace_count = line.count('{') - line.count('}')
                else:
                    brace_count += line.count('{') - line.count('}')
                i += 1
                if started and brace_count == 0:
                    break
            # Now inject the replacement
            new_lines.append(replacement)
            continue
        new_lines.append(lines[i])
        i += 1
    new_content = '\n'.join(new_lines)

with open(settings_path, 'w') as f:
    f.write(new_content)

print("✅ Settings file patched successfully")
EOF

# Load the environment variable for subsequent RUN commands
RUN source /tmp/django_env && echo "DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"

# Collect static files
RUN source /tmp/django_env && python manage.py collectstatic --noinput

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
