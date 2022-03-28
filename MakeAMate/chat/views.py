from django.shortcuts import render
from django.contrib.auth.models import User
from chat.models import ChatRoom
from principal.models import Mates
from django.db.models import Q

def index(request):
    lista_mates = notificaciones_mates(request)
    lista_chat = []
    chats = ChatRoom.objects.all()
    for c in chats:
        if request.user in c.participants.all():
            lista_chat.append(c)
    lista_usuarios = []
    for c in lista_chat:
        participantes = c.participants.filter(~Q(id=request.user.id))
        lista_usuarios.append(participantes[0])
    return render(request, 'chat/index.html',{'users': lista_mates, 'chats':lista_chat, 'nombrechats':lista_usuarios})

def grupos(request):
    lista_mates = notificaciones_mates(request)
    return render(request, 'chat/grupos.html',{'users': lista_mates})


def room(request, room_name):

    chatroom = ChatRoom.objects.filter(name = room_name)[0]
    lista_participantes = []

    for p in chatroom.participants.all():
        lista_participantes.append(p.username)

    # Comprobación si el usuario pertenece a los participantes de ese grupo
    if request.user.username in lista_participantes:
        return render(request, 'chat/room.html', {
            'room_name': room_name
        })
    else:
        return index(request)

def crear_sala(room_participants):
    room = ChatRoom.objects.create()
    room.participants.set(room_participants)

def crear_sala_grupo(group_name, room_participants):
    room = ChatRoom.objects.create(room_name = group_name)
    room.participants.set(room_participants)



def notificaciones_mates(request):
    loggeado= request.user
    lista_usuarios=User.objects.filter(~Q(id=loggeado.id))
    lista_mates=[]
    for i in lista_usuarios:
        try:
            mate1=Mates.objects.get(mate=True,userEntrada=loggeado,userSalida=i)
            mate2=Mates.objects.get(mate=True,userEntrada=i,userSalida=loggeado)
            lista_mates.append(mate1.userSalida)
        except Mates.DoesNotExist:
            print("NO EXISTE MATE CON "+ str(i))
    return lista_mates