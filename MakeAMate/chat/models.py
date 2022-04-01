from email.policy import default
from django.db import models
from django.contrib.auth.models import User
import base64, os


class Chat(models.Model):
    content = models.TextField(max_length=2000)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey('ChatRoom', on_delete=models.CASCADE)

    def __str__(self):
        return self.content

class ChatRoom(models.Model):
    name = models.AutoField(primary_key=True)
    participants = models.ManyToManyField(User)
    publicKey = models.TextField(default=base64.urlsafe_b64encode(os.urandom(32)).decode())
    room_name = models.CharField(max_length=255, blank=True, default='')

    def group(self):
        if len(self.participants.all()) > 2:
            return True
        else:
            return False
