from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from chat.models import ChatRoom
from principal.models import Mates, Usuario
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
        lista_aux = []
        if c.group == True:
            for p in participantes[0]:
                usuarioApp = Mates.objects.filter(id = p.id)
                lista_aux.append(usuarioApp)
            lista_usuarios.append(lista_aux)
        else:
            usuario = Usuario.objects.filter(id = participantes[0].id)[0]
            print(usuario.edad)
            lista_usuarios.append(usuario)
    print(lista_chat)
    print(lista_usuarios)
    return render(request, 'chat/index.html',{'users': lista_mates, 'chats':lista_chat, 'nombrechats':lista_usuarios})


def room(request, room_name):

    chatroom = ChatRoom.objects.filter(name = room_name)[0]
    lista_participantes = []

    for p in chatroom.participants.all():
        lista_participantes.append(p.username)


    # Comprobación si el usuario pertenece a los participantes de ese grupo
    if request.user.username in lista_participantes:
        return render(request, 'chat/room.html', {'room_name': room_name})
    else:
        return redirect('/chat')

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