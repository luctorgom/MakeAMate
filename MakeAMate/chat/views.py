from django.shortcuts import render
from django.contrib.auth.models import User
from chat.models import ChatRoom
from principal.models import Mates

def index(request):
    lista_mates = notificaciones_mates(request)
    return render(request, 'chat/index.html',{'users': lista_mates})


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
        return render(request, 'chat/index.html')

def crear_sala(room_participants):
    room = ChatRoom.objects.create()
    room.participants.set(room_participants)



def notificaciones_mates(request):
    loggeado= request.user
    lista_usuarios=User.objects.filter(~Q(id=loggeado.id))
    print("Usuario loggeado: " + str(loggeado))
    print(loggeado)
    print("Lista usuarios: " + str(lista_usuarios))
    print(lista_usuarios)
    lista_mates=[]
    for i in lista_usuarios:
        try:
            mate1=Mates.objects.get(mate=True,userEntrada=loggeado,userSalida=i)
            mate2=Mates.objects.get(mate=True,userEntrada=i,userSalida=loggeado)
            print("Mate 1: " + str(mate1))
            print("Mate 2: " + str(mate2))
            lista_mates.append(mate1.userSalida)
        except Mates.DoesNotExist:
            print("NO EXISTE MATE CON "+ str(i))
    print("lista_mates: " + str(lista_mates))
    return lista_mates