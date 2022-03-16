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
    name = models.CharField(max_length=255)
    #participants = models.ManyToManyField(User)

    def __str__(self):
        return self.name


#habría que cambiar el user por el perfil?