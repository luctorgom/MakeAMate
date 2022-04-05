from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from chat.models import ChatRoom
from principal.models import Mates, Usuario
from django.db.models import Q
from chat.forms import CrearGrupo
from django.core.exceptions import PermissionDenied


def index(request):
    if request.user.is_authenticated:
        #form
        form = CrearGrupo(notificaciones_mates(request), request.GET,request.FILES)
        crear_grupo_form(request, form)

        lista_mates = notificaciones_mates(request)
        if len(lista_mates)>0:
            lista_chat = []
            chats = ChatRoom.objects.all()
            for c in chats:
                if request.user in c.participants.all():
                    lista_chat.append(c)
            lista_usuarios = []
            usuarios = Usuario.objects.filter(~Q(id=request.user.id))
            for u in usuarios:
                lista_usuarios.append(u)
            return render(request, 'chat/index.html',{'users': lista_mates, 'chats':lista_chat, 'nombrechats':lista_usuarios,'form':form})
        else:
            raise PermissionDenied
    else:
        return redirect("/login")

def room(request, room_name):
    if request.user.is_authenticated:
        #Comprobación para que no se fuerce la URL
        try:
            chatroom = ChatRoom.objects.filter(name = room_name)[0]
            lista_participantes = []
        except IndexError:
            raise PermissionDenied

        #form
        form = CrearGrupo(notificaciones_mates(request), request.GET,request.FILES)
        crear_grupo_form(request, form)

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

        for p in chatroom.participants.all():
            lista_participantes.append(p.username)
        nombre_sala = ""
        es_grupo = False
        if chatroom.group():
            nombre_sala = chatroom.room_name
            es_grupo = True
        else:
            nombre_sala = chatroom.participants.all().filter(~Q(id=request.user.id))[0].username

        # Comprobación si el usuario pertenece a los participantes de ese grupo
        if request.user.username in lista_participantes :
            return render(request, 'chat/room.html', {'room_name': room_name,'users': lista_mates, 'chats':lista_chat, 'nombrechats':lista_usuarios, 'form':form, 'nombre_sala':nombre_sala, 'es_grupo':es_grupo})
        else:
            raise PermissionDenied
    else:
        return redirect("/login")


def crear_grupo_form(request, form):
    if request.method=='POST':
        form = CrearGrupo(notificaciones_mates(request), request.POST)
        if form.is_valid():
            if len(form.cleaned_data['Personas'])>1:
                lista = form.cleaned_data['Personas']
                nombre = form.cleaned_data['Nombre']
                lista.append(request.user.id)
                crear_sala_grupo(nombre, lista)





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
            pass
    return lista_mates



