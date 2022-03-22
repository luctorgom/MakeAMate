from django.shortcuts import render
from django.contrib.auth.models import User
from chat.models import ChatRoom

def index(request):
    return render(request, 'chat/index.html',{'users': User.objects.all().exclude(username = request.user.username)})
    #Ese users tiene que cambiar de todos los usuarios a solo los que han hecho mate

def room(request, room_name):
    current_user = request.user.username
    chatroom = ChatRoom.objects.filter(name = room_name)[0]
    lista = []
    for p in chatroom.participants.all():
        lista.append(p.username)
    if current_user in lista:
        return render(request, 'chat/room.html', {
            'room_name': room_name
        })
    else:
        return render(request, 'chat/index.html')
