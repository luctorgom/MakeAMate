from django.shortcuts import render
from django.contrib.auth.models import User

def index(request):
    return render(request, 'chat/index.html',{'users': User.objects.all().exclude(username = request.user.username)})
    #Ese users tiene que cambiar de todos los usuarios a solo los que han hecho mate

def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })
