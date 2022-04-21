import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from chat.models import Chat,ChatRoom, LastConnection
from cryptography.fernet import Fernet
from datetime import datetime

class ChatConsumer(WebsocketConsumer):

    def connect(self):
        
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        user = self.scope['user']

        chatroom = ChatRoom.objects.filter(name = self.scope['url_route']['kwargs']['room_name'],participants = user)[0]

        last_connection = LastConnection.objects.get_or_create(name = chatroom, user = user)[0]
        last_connection.timestamp = datetime.now().isoformat()
        
        # Comprobación si el usuario pertenece a los participantes de ese grupo
        #if chatroom:
            # Join room group
        async_to_sync(self.channel_layer.group_add)(
        self.room_group_name,
        self.channel_name
        )
        self.accept()
        room = ChatRoom.objects.get_or_create(name = self.room_name)
        self.get_all_messages()

    def disconnect(self, close_code):
        chat = ChatRoom.objects.get_or_create(name = self.scope['url_route']['kwargs']['room_name'])[0]
        last_connection = LastConnection.objects.get_or_create(name = chat, user = self.scope['user'])[0]

        last_connection.timestamp = datetime.now().isoformat()
        last_connection.save()
        
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
    
        if message!="":
            self.store_message(message)
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
        if message!="":
            self.send(text_data=json.dumps({
                "type": "chat_message",
                'name': username,
                'message': message
            }))
    
    def store_message(self,text):
        room = ChatRoom.objects.get_or_create(name = self.scope['url_route']['kwargs']['room_name'])[0]
        f = Fernet(room.publicKey.encode())
        token = f.encrypt(bytes(text, encoding='utf-8'))
        chat = Chat.objects.create(
            content = token.decode(),
            user = self.scope['user'],
            room = room
        )
        room.last_message = chat.timestamp 
        room.save()
    
    def get_all_messages(self):
        chatroom = ChatRoom.objects.filter(name = self.scope['url_route']['kwargs']['room_name'])[0]
        mess = Chat.objects.filter(room = chatroom).order_by('timestamp')
        for m in mess:
            mensaje = Fernet(chatroom.publicKey.encode()).decrypt(bytes(m.content,'utf-8'))
            data = {
                "type": "chat_message",
                'name': m.user.username,
                'message': mensaje.decode()
            }
            self.send(text_data=json.dumps(data))
