from django.urls import re_path

from . import consumers

#Este script redirige el websocket a la vista en la que se crea el chat 
websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]