"""
ASGI config for apc_project.
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import re_path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apc_project.settings")

from apps.messaging.consumers import ChatConsumer
from apps.meetings.consumers import MeetingSignalingConsumer
from infrastructure.websockets.notification_consumer import NotificationConsumer
from infrastructure.websockets.presence_consumer import PresenceConsumer
from infrastructure.websockets.live_streaming_consumer import LiveStreamingConsumer
from infrastructure.websockets.location_consumer import LocationConsumer
# NEW consumers
from infrastructure.websockets.sync_consumer import SyncConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_id>[0-9a-f-]+)/$", ChatConsumer.as_asgi()),
    re_path(r"ws/meeting/(?P<meeting_id>[0-9-]+)/$", MeetingSignalingConsumer.as_asgi()),
    re_path(r"ws/notifications/$", NotificationConsumer.as_asgi()),
    re_path(r"ws/presence/$", PresenceConsumer.as_asgi()),
    re_path(r"ws/live/(?P<stream_id>[0-9a-f-]+)/$", LiveStreamingConsumer.as_asgi()),
    re_path(r"ws/location/(?P<user_id>[0-9a-f-]+)/$", LocationConsumer.as_asgi()),
    # NEW
    re_path(r"ws/sync/(?P<device_id>[0-9a-f-]+)/$", SyncConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
