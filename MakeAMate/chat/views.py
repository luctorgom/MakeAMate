from django.shortcuts import render
from django.contrib.auth.models import User
from chat.models import ChatRoom
from principal.models import Mates
from principal.views import notificaciones_mates

def index(request):
    lista_mates = notificaciones_mates(request)
    return render(request, 'chat/index.html',{'users': lista_mates})


def room(request, room_name):

    current_user = request.user.username
    current_participant = request.user.id
    room_participants = []
    room_participants.append(current_participant)
    crear_sala(room_name, room_participants)

    chatroom = ChatRoom.objects.filter(name = room_name)[0]
    lista_participantes = []
    for p in chatroom.participants.all():
        lista_participantes.append(p.username)

    # Comprobación si el usuario pertenece a los participantes de ese grupo
    if current_user in lista_participantes:
        return render(request, 'chat/room.html', {
            'room_name': room_name
        })
    else:
        return render(request, 'chat/index.html')

def crear_sala(room_name, room_participants):

    room = ChatRoom.objects.get_or_create(name = room_name)[0]
    print(room)
    room.participants.set(room_participants)
