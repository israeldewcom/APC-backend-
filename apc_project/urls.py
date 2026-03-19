"""
APC Private Connect - Master URL Configuration (Enhanced)
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerUIView, SpectacularRedocView

def health_check(request):
    from django.db import connection
    from django.core.cache import cache
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False
    try:
        cache.set('health', 'ok', timeout=10)
        redis_ok = cache.get('health') == 'ok'
    except Exception:
        redis_ok = False
    status_code = 200 if (db_ok and redis_ok) else 503
    return JsonResponse({
        'status': 'healthy' if status_code == 200 else 'degraded',
        'database': 'ok' if db_ok else 'error',
        'cache': 'ok' if redis_ok else 'error',
        'version': '1.0.0',
        'platform': 'APC Private Connect',
    }, status=status_code)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check),

    # API v1
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/verification/', include('apps.nin_verification.urls')),
    path('api/v1/posts/', include('apps.posts.urls')),
    path('api/v1/messages/', include('apps.messaging.urls')),
    path('api/v1/groups/', include('apps.groups.urls')),
    path('api/v1/meetings/', include('apps.meetings.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/media/', include('apps.media.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/security/', include('apps.security.urls')),

    # NEW API endpoints (original)
    path('api/v1/stories/', include('apps.stories.urls')),
    path('api/v1/live/', include('apps.live_streaming.urls')),
    path('api/v1/hashtags/', include('apps.hashtags.urls')),
    path('api/v1/reels/', include('apps.reels.urls')),
    path('api/v1/events/', include('apps.events.urls')),
    path('api/v1/marketplace/', include('apps.marketplace.urls')),
    path('api/v1/voice-notes/', include('apps.voice_notes.urls')),
    path('api/v1/broadcast/', include('apps.broadcast.urls')),
    path('api/v1/close-friends/', include('apps.close_friends.urls')),
    path('api/v1/data-export/', include('apps.data_export.urls')),
    path('api/v1/search/', include('apps.search.urls')),
    path('api/v1/location/', include('apps.location.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/moderation/', include('apps.moderation.urls')),
    path('api/v1/i18n/', include('apps.i18n.urls')),
    path('api/v1/creator-analytics/', include('apps.creator_analytics.urls')),
    path('api/v1/scheduled-posts/', include('apps.scheduled_posts.urls')),

    # NEW API endpoints (upgrade)
    path('api/v1/organizations/', include('apps.multi_tenant.urls')),
    path('api/v1/rbac/', include('apps.rbac.urls')),
    path('api/v1/encryption/', include('apps.encryption.urls')),
    path('api/v1/biometrics/', include('apps.biometrics.urls')),
    path('api/v1/recommendations/', include('apps.recommendations.urls')),
    path('api/v1/ai/', include('apps.ai.urls')),
    path('api/v1/sync/', include('apps.sync.urls')),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerUIView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
