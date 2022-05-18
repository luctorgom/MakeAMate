from email.policy import default
from django.db import models
from django.contrib.auth.models import User
import base64, os
from datetime import datetime
from django.utils import timezone
from principal.models import Usuario

class Chat(models.Model):
    content = models.TextField(max_length=2000)
    timestamp = models.DateTimeField(default=datetime.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey('ChatRoom', on_delete=models.CASCADE)

    def __str__(self):
        return self.content

class ChatRoom(models.Model):
    name = models.AutoField(primary_key=True)
    participants = models.ManyToManyField(User)
    publicKey = models.TextField(default=base64.urlsafe_b64encode(os.urandom(32)).decode())
    room_name = models.CharField(max_length=255, blank=True, default='')
    last_message = models.DateTimeField(default=timezone.now)

    def group(self):
        if len(self.participants.all()) > 2:
            return True
        else:
            return False

    def get_usuarios(self):
        return [Usuario.objects.get(usuario=u) for u in self.participants.all()]

class LastConnection(models.Model):
    name = models.ForeignKey('ChatRoom', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=datetime.now)
