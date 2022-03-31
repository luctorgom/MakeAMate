from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from chat.models import ChatRoom
from principal.models import Mates, Usuario
from django.db.models import Q
from chat.forms import CrearGrupo

def index(request):
    lista_mates = notificaciones_mates(request)
    lista_chat = []
    chats = ChatRoom.objects.all()
    for c in chats:
        if request.user in c.participants.all():
            lista_chat.append(c)
    lista_usuarios = []
    usuarios = Usuario.objects.filter(~Q(id=request.user.id))
    for u in usuarios:
        lista_usuarios.append(u)
    return render(request, 'chat/index.html',{'users': lista_mates, 'chats':lista_chat, 'nombrechats':lista_usuarios})

def grupos(request):
    lista_mates = notificaciones_mates(request)
    return render(request, 'chat/grupos.html',{'users': lista_mates})


def room(request, room_name):
    #form
    form = CrearGrupo(notificaciones_mates(request), request.GET,request.FILES)
    if request.method=='POST':
        form = CrearGrupo(notificaciones_mates(request), request.POST)
        if form.is_valid():
            lista = form.cleaned_data['Grupo']
            nombre = form.cleaned_data['Nombre']
            lista.append(request.user.id)
            crear_sala_grupo(nombre, lista)
        return redirect('/chat')

    #lista chats
    lista_mates = notificaciones_mates(request)
    lista_chat = []
    chats = ChatRoom.objects.all()
    for c in chats:
        if request.user in c.participants.all():
            lista_chat.append(c)
    lista_usuarios = []
    usuarios = Usuario.objects.filter(~Q(id=request.user.id))
    for u in usuarios:
        lista_usuarios.append(u)

    chatroom = ChatRoom.objects.filter(name = room_name)[0]
    lista_participantes = []
    
    for p in chatroom.participants.all():
        lista_participantes.append(p.username)

    # Comprobación si el usuario pertenece a los participantes de ese grupo
    if request.user.username in lista_participantes:
        return render(request, 'chat/room.html', {'room_name': room_name,'users': lista_mates, 'chats':lista_chat, 'nombrechats':lista_usuarios, 'form':form, 'users':notificaciones_mates(request)})
    else:
        return redirect('/chat'),


def crear_grupo_form(request):
    form = CrearGrupo(notificaciones_mates(request), request.GET,request.FILES)
    if request.method=='POST':
        form = CrearGrupo(notificaciones_mates(request), request.POST)
        if form.is_valid():
            lista = form.cleaned_data['Grupo']
            nombre = form.cleaned_data['Nombre']
            lista.append(request.user.id)
            crear_sala_grupo(nombre, lista)
        return redirect('/chat')

    return render(request, 'chat/form.html',{'form':form, 'users':notificaciones_mates(request)})



#Funciones para obtener atributos
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



