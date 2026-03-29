import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tttmail.settings")
django.setup()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path
from tttmail.middlewares.channels import ChannelsTokenAuthMiddleware
from core.consumers import NotificationConsumer

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        ChannelsTokenAuthMiddleware(
            URLRouter([
                path("ws/notifications/", NotificationConsumer.as_asgi()),
                path("hrm/ws/notifications/", NotificationConsumer.as_asgi()),
            ])
        )
    ),
})
