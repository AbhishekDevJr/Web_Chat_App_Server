from django.urls import re_path, path
from . import consumer

websocket_urlpatterns = [
    # re_path(r"ws/chat/(?p<room_id>\w+)/$", consumer.ChatConsumer.as_asgi()),
    path('ws/chat/<str:room_id>', consumer.ChatConsumer.as_asgi())
]