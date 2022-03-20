from pyexpat import model
from django.shortcuts import render
from principal import models
from .models import Chat

def index(request):
    return render(request, 'index.html')

def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })
