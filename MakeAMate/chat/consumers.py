import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.consumer import AsyncConsumer
from chat.models import Chat,ChatRoom
from django.contrib.auth.models import User


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        room = ChatRoom.objects.get_or_create(name = self.room_name)
        self.get_all_messages()



    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']


        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'name': self.scope['user'].username,
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        username = event['name']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            "type": "chat_message",
            'name': username,
            'message': message
        }))
        self.store_message(message)
    
    def store_message(self,text):
        chatroom = (ChatRoom.objects.filter(name = self.scope['url_route']['kwargs']['room_name'])[0])
        Chat.objects.create(
            content = text,
            user = self.scope['user'],
            room = ChatRoom.objects.get_or_create(name = self.scope['url_route']['kwargs']['room_name'])[0]
        )

    #El chatroom se guarda una vez que se envía el primer mensaje, lo suyo sería que cuando se creen grupos se guarde al inicio
    #Faltan añadir a los usuarios implicados


    def get_all_messages(self):
        chatroom = ChatRoom.objects.filter(name = self.scope['url_route']['kwargs']['room_name'])[0]
        mess = Chat.objects.filter(room = chatroom).order_by('timestamp')
        for  m in mess:
            data = {
                "type": "chat_message",
                'name': m.user.username,
                'message': m.content
            }
            self.send(text_data=json.dumps(data))
