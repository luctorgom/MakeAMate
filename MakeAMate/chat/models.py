from django.db import models
from django.contrib.auth.models import User

class Chat(models.Model):
    content = models.CharField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey('ChatRoom', on_delete=models.CASCADE)

    def __str__(self):
        return self.content

class ChatRoom(models.Model):
    name = models.AutoField(primary_key=True)
    participants = models.ManyToManyField(User)
    room_name = models.CharField(max_length=255, blank=True, default='')
    @classmethod
    def group(self):
        if len(self.participants)>2:
            return True
        else:
            return False