from django.urls import re_path
from .consumers import ChatConsumer, CallConsumer

websocket_urlpatterns = [
    # 1-on-1 chat
    re_path(r"ws/chat/(?P<username>\w+)/$", ChatConsumer.as_asgi()),

    # Group chat
    re_path(r"ws/group/(?P<group_id>\d+)/$", ChatConsumer.as_asgi()),

    # WebRTC signaling (calls)
    # NOTE: username in URL is NOT used anymore — CallConsumer uses scope["user"]
    re_path(r"ws/call/(?P<username>\w+)/$", CallConsumer.as_asgi()),
]
