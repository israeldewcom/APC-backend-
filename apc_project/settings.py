"""
APC Private Connect - Production Settings (Enhanced)
"""
import os
from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── SECURITY ────────────────────────────────────────────────────────────────
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# ─── APPLICATIONS ────────────────────────────────────────────────────────────
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'channels',
    'django_filters',
    'drf_spectacular',
    'storages',
    'django_celery_beat',
    'django_celery_results',
    'parler',
    'django_elasticsearch_dsl',
    'guardian',
    'cryptography',
]

LOCAL_APPS = [
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

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ─── MIDDLEWARE ──────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.security.SecurityHeadersMiddleware',
    'core.middleware.audit.AuditLogMiddleware',
    'core.middleware.rate_limit.RateLimitMiddleware',
    'core.middleware.device.DeviceTrackingMiddleware',
    'core.middleware.i18n.LanguageMiddleware',
    'core.middleware.multi_tenant.MultiTenantMiddleware',
]

ROOT_URLCONF = 'apc_project.urls'
WSGI_APPLICATION = 'apc_project.wsgi.application'
ASGI_APPLICATION = 'apc_project.asgi.application'
AUTH_USER_MODEL = 'users.User'

# ─── TEMPLATES ───────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ─── DATABASE ────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='apc_db'),
        'USER': config('DB_USER', default='apc_user'),
        'PASSWORD': config('DB_PASSWORD', default='apc_password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',
        },
        'ATOMIC_REQUESTS': True,
    },
    'analytics': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('ANALYTICS_DB_NAME', default='apc_analytics'),
        'USER': config('DB_USER', default='apc_user'),
        'PASSWORD': config('DB_PASSWORD', default='apc_password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 300,
    }
}
DATABASE_ROUTERS = ['core.utils.db_router.AnalyticsRouter']

# ─── REDIS & CACHE ───────────────────────────────────────────────────────────
REDIS_URL = config('REDIS_URL', default='redis://localhost:6379')
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'{REDIS_URL}/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'CONNECTION_POOL_KWARGS': {'max_connections': 100, 'retry_on_timeout': True},
        },
        'KEY_PREFIX': 'apc',
        'TIMEOUT': 300,
    },
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'{REDIS_URL}/1',
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
        'KEY_PREFIX': 'apc_session',
        'TIMEOUT': 86400,
    },
    'rate_limit': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'{REDIS_URL}/2',
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
        'KEY_PREFIX': 'apc_rate',
        'TIMEOUT': 3600,
    },
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'
SESSION_COOKIE_AGE = 86400 * 7
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ─── CHANNELS (WebSocket) ───────────────────────────────────────────────────
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [f'{REDIS_URL}/3'],
            'capacity': 1500,
            'expiry': 10,
        },
    },
}

# ─── CELERY ─────────────────────────────────────────────────────────────────
CELERY_BROKER_URL = f'{REDIS_URL}/4'
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='django-db')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Lagos'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ROUTES = {
    'apps.notifications.tasks.*': {'queue': 'notifications'},
    'apps.media.tasks.*': {'queue': 'media'},
    'apps.analytics.tasks.*': {'queue': 'analytics'},
    'apps.meetings.tasks.*': {'queue': 'meetings'},
    'apps.security.tasks.*': {'queue': 'security'},
    'apps.stories.tasks.*': {'queue': 'stories'},
    'apps.live_streaming.tasks.*': {'queue': 'live'},
    'apps.moderation.tasks.*': {'queue': 'moderation'},
    'apps.data_export.tasks.*': {'queue': 'export'},
    'apps.scheduled_posts.tasks.*': {'queue': 'scheduled'},
    'apps.recommendations.tasks.*': {'queue': 'recommendations'},
    'apps.ai.tasks.*': {'queue': 'ai'},
    'apps.sync.tasks.*': {'queue': 'sync'},
}

# ─── REST FRAMEWORK ─────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'core.utils.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'core.utils.throttle.BurstRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'burst': '60/min',
        'auth': '10/min',
        'nin_verify': '5/hour',
        'fingerprint': '10/hour',
        'story_create': '50/day',
        'live_start': '10/day',
    },
    'EXCEPTION_HANDLER': 'core.utils.exceptions.custom_exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ─── JWT SETTINGS ───────────────────────────────────────────────────────────
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'TOKEN_OBTAIN_SERIALIZER': 'apps.authentication.serializers.CustomTokenObtainSerializer',
}

# ─── CORS ───────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000', cast=Csv())
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization', 'content-type',
    'dnt', 'origin', 'user-agent', 'x-csrftoken', 'x-requested-with',
    'x-device-id', 'x-fingerprint-token', 'accept-language',
]

# ─── AWS S3 STORAGE ─────────────────────────────────────────────────────────
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='apc-media')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default=f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com')
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400', 'ACL': 'private'}
AWS_DEFAULT_ACL = 'private'
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 3600
AWS_S3_FILE_OVERWRITE = False
AWS_S3_VERIFY = True

STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
        'OPTIONS': {
            'bucket_name': AWS_STORAGE_BUCKET_NAME,
            'location': 'media',
        }
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ─── EMAIL ──────────────────────────────────────────────────────────────────
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='APC Private Connect <noreply@apcconnect.ng>')
EMAIL_SUBJECT_PREFIX = '[APC Connect] '

# ─── FIREBASE (Push Notifications) ──────────────────────────────────────────
FIREBASE_CREDENTIALS_PATH = config('FIREBASE_CREDENTIALS_PATH', default='')
FCM_SERVER_KEY = config('FCM_SERVER_KEY', default='')

# ─── NIN VERIFICATION ───────────────────────────────────────────────────────
NIMC_API_BASE_URL = config('NIMC_API_BASE_URL', default='https://api.nimc.gov.ng/v1')
NIMC_API_KEY = config('NIMC_API_KEY', default='')
NIMC_API_SECRET = config('NIMC_API_SECRET', default='')
NIN_VERIFICATION_ENABLED = config('NIN_VERIFICATION_ENABLED', default=True, cast=bool)

# ─── PAYMENT GATEWAY (Paystack) ─────────────────────────────────────────────
PAYSTACK_PUBLIC_KEY = config('PAYSTACK_PUBLIC_KEY', default='')
PAYSTACK_SECRET_KEY = config('PAYSTACK_SECRET_KEY', default='')

# ─── GOOGLE CLOUD VISION (Moderation) ───────────────────────────────────────
GOOGLE_APPLICATION_CREDENTIALS = config('GOOGLE_APPLICATION_CREDENTIALS', default='')

# ─── LOCATION SERVICES ──────────────────────────────────────────────────────
GOOGLE_MAPS_API_KEY = config('GOOGLE_MAPS_API_KEY', default='')

# ─── INTERNATIONALIZATION ───────────────────────────────────────────────────
PARLER_LANGUAGES = {
    1: (
        {'code': 'en',},
        {'code': 'ha',},
        {'code': 'yo',},
        {'code': 'ig',},
    ),
    'default': {
        'fallbacks': ['en'],
        'hide_untranslated': False,
    }
}
LANGUAGE_CODE = config('LANGUAGE_CODE', default='en-us')
TIME_ZONE = config('TIME_ZONE', default='Africa/Lagos')
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ─── SECURITY SETTINGS ──────────────────────────────────────────────────────
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'core.validators.password.ApcPasswordValidator'},
]

# ─── LOGGING ────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            '()': 'core.utils.logging.JsonFormatter',
        },
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'verbose'},
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/apc_backend.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'json',
        },
        'security_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/security.log',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 20,
            'formatter': 'json',
        },
        'audit_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/audit.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 30,
            'formatter': 'json',
        },
    },
    'loggers': {
        'django': {'handlers': ['console', 'file'], 'level': 'INFO'},
        'apc.security': {'handlers': ['security_file', 'console'], 'level': 'WARNING', 'propagate': False},
        'apc.audit': {'handlers': ['audit_file'], 'level': 'INFO', 'propagate': False},
        'apc.api': {'handlers': ['console', 'file'], 'level': 'INFO'},
    },
}

# ─── API DOCUMENTATION ──────────────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    'TITLE': 'APC Private Connect API',
    'DESCRIPTION': 'Enterprise Backend API for APC Private Social Platform',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [{'BearerAuth': []}],
}

# ─── APP SPECIFIC SETTINGS ──────────────────────────────────────────────────
APC_SETTINGS = {
    'MAX_PROFILE_PICTURE_SIZE': 5 * 1024 * 1024,
    'MAX_POST_MEDIA_SIZE': 100 * 1024 * 1024,
    'MAX_MESSAGE_ATTACHMENT_SIZE': 50 * 1024 * 1024,
    'MAX_GROUP_MEMBERS': 5000,
    'MAX_MEETING_PARTICIPANTS': 500,
    'POST_FEED_CACHE_TTL': 300,
    'USER_PROFILE_CACHE_TTL': 600,
    'OTP_EXPIRY_MINUTES': 10,
    'MAX_LOGIN_ATTEMPTS': 5,
    'LOCKOUT_DURATION_MINUTES': 30,
    'FINGERPRINT_REQUIRED_FOR_ADMIN_ACTIONS': True,
    'NIN_REQUIRED_FOR_FULL_ACCESS': True,
    'MESSAGE_ENCRYPTION_ENABLED': True,
    'AUDIT_ALL_ACTIONS': True,
    'ALLOWED_MEDIA_TYPES': [
        'image/jpeg', 'image/png', 'image/gif', 'image/webp',
        'video/mp4', 'video/webm', 'video/avi',
        'audio/mpeg', 'audio/wav', 'audio/ogg',
        'application/pdf', 'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    ],
    'STORY_EXPIRY_HOURS': 24,
    'REEL_MAX_DURATION_SECONDS': 90,
    'LIVE_MAX_DURATION_HOURS': 4,
    'MARKETPLACE_LISTING_EXPIRY_DAYS': 30,
    'PAYMENT_MIN_AMOUNT': 100,
    'PAYMENT_MAX_AMOUNT': 1000000,
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── NEW SETTINGS FOR UPGRADE ───────────────────────────────────────────────
MULTI_TENANT_DOMAIN_PATTERN = config('DEFAULT_DOMAIN', default='apcconnect.ng')
TENANT_SCHEMA_PREFIX = config('TENANT_SCHEMA_PREFIX', default='tenant')

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': f"{config('ELASTICSEARCH_HOST', default='localhost')}:{config('ELASTICSEARCH_PORT', default='9200')}"
    },
}

ENCRYPTION_SALT = config('ENCRYPTION_SALT', default='change-this-salt').encode()
FACE_RECOGNITION_TOLERANCE = config('FACE_RECOGNITION_TOLERANCE', default=0.6, cast=float)
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
AI_MODEL_PATH = config('AI_MODEL_PATH', default='/app/models/')
TURN_SERVER_URL = config('TURN_SERVER_URL', default='')
TURN_USERNAME = config('TURN_USERNAME', default='')
TURN_PASSWORD = config('TURN_PASSWORD', default='')

# ─── TESTING ────────────────────────────────────────────────────────────────
if DEBUG:
    INSTALLED_APPS += ['django_extensions']
