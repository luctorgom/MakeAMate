from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from chat.models import ChatRoom, Chat
from principal.models import Mate, Usuario
from django.db.models import Q
from chat.forms import CrearGrupo
from django.core.exceptions import PermissionDenied
from cryptography.fernet import Fernet
from chat.models import Chat,ChatRoom,LastConnection
from django.views.decorators.cache import never_cache
from datetime import timedelta


@never_cache
def index(request):
    if request.user.is_authenticated:
        if Usuario.objects.get(usuario = request.user).sms_validado == False:
            return redirect("registerSMS")
        lista_mates = notificaciones_mates(request)
        user = request.user
        
        #form
        form, mensaje_grupo = crear_grupo_form(request)
        if form is None:
            return redirect(index)

        if len(lista_mates)>0:

            #lista chats
            lista_chat = []
            chats = ChatRoom.objects.all().order_by('-last_message')

            for c in chats:
                lista_chat_aux = []
                if request.user in c.participants.all():
                    lista_chat_aux.append(c)
                    try:
                        lista_chat_aux.append(Fernet(c.publicKey.encode()).decrypt(bytes(Chat.objects.filter(timestamp = c.last_message)[0].content,'utf-8')).decode())
                    except IndexError:
                        lista_chat_aux.append("No se ha enviado ningún mensaje")
                lista_chat.append(lista_chat_aux)
            return render(request, 'chat/index.html',{'notificaciones':notificaciones(request),'users': lista_mates, 'chats':lista_chat,
                                                    'usuario_actual': Usuario.objects.filter(usuario=request.user)[0], 'form':form,
                                                    'error_grupo':mensaje_grupo})
        else:
            return render(request, 'chat/index.html',{'notificaciones':[],'users': [], 'chats':[],'usuario_actual': Usuario.objects.filter(usuario=request.user)[0],
                                                    'form':form,'error_grupo':mensaje_grupo})
    else:
        return redirect("/login")

@never_cache
def room(request, room_name):
    if request.user.is_authenticated:
        if Usuario.objects.get(usuario = request.user).sms_validado == False:
            return redirect("registerSMS")
        #Comprobación para que no se fuerce la URL
        try:
            chatroom = ChatRoom.objects.filter(name = room_name)[0]
        except IndexError:
            raise PermissionDenied

        #form
        form, mensaje_grupo = crear_grupo_form(request)
        if form is None:
            return redirect(index)

        #lista chats
        lista_mates = notificaciones_mates(request)
        lista_chat = []
        chats = ChatRoom.objects.all().order_by('-last_message')
        for c in chats:
            lista_chat_aux = []
            if request.user in c.participants.all():
                lista_chat_aux.append(c)
                try:
                    lista_chat_aux.append(Fernet(c.publicKey.encode()).decrypt(bytes(Chat.objects.filter(timestamp = c.last_message)[0].content,'utf-8')).decode())
                except IndexError:
                    lista_chat_aux.append("No se ha enviado ningún mensaje")
            lista_chat.append(lista_chat_aux)
        
        usuario_opuesto = ""
        if chatroom.group()== False:
            usuario_opuesto = Usuario.objects.filter(usuario=chatroom.participants.all().filter(~Q(id=request.user.id))[0])[0]

        # Comprobación si el usuario pertenece a los participantes de ese grupo
        if request.user in chatroom.participants.all() :

            return render(request, 'chat/room.html', {'room_name': room_name,'users': lista_mates, 'chats':lista_chat, 'form':form,
                                                    'usuario_actual':Usuario.objects.filter(usuario=request.user)[0], 'usuario_opuesto':usuario_opuesto,
                                                    'error_grupo':mensaje_grupo, 'chat_actual':chatroom})
        else:
            raise PermissionDenied
    else:
        return redirect("/login")


def crear_grupo_form(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    if Usuario.objects.get(usuario = request.user).sms_validado == False:
        return redirect("registerSMS")
    if request.method=='POST':
        form = CrearGrupo(notificaciones_mates(request), request.POST)
        if form.is_valid():
            if len(form.cleaned_data['Personas'])>1:
                lista = form.cleaned_data['Personas']
                nombre = form.cleaned_data['Nombre']
                lista.append(request.user.id)
                crear_sala_grupo(nombre, lista)
                return None, None
            else: return form,  "Debe seleccionar al menos 2 usuarios"
        else: return form, "Debe seleccionar al menos 2 usuarios"
    return CrearGrupo(notificaciones_mates(request)),None





#Funciones para obtener atributos
def crear_sala(room_participants):
    room = ChatRoom.objects.create()
    room.participants.set(room_participants)

def crear_sala_grupo(group_name, room_participants):
    room = ChatRoom.objects.create(room_name = group_name)
    room.participants.set(room_participants)

def notificaciones_mates(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    if Usuario.objects.get(usuario = request.user).sms_validado == False:
        return redirect("registerSMS")
    loggeado= request.user
    lista_usuarios=User.objects.filter(~Q(id=loggeado.id))
    lista_mates=[]
    for i in lista_usuarios:
        try:
            mate1=Mate.objects.get(mate=True,userEntrada=loggeado,userSalida=i)
            mate2=Mate.objects.get(mate=True,userEntrada=i,userSalida=loggeado)
            lista_mates.append(mate1.userSalida)
        except Mate.DoesNotExist:
            pass
    return lista_mates

def notificaciones_mates2(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    if Usuario.objects.get(usuario = request.user).sms_validado == False:
        return redirect("registerSMS")
    lista_notificaciones=[]
    loggeado= request.user
    perfil=Usuario.objects.get(usuario=loggeado)
    es_premium= perfil.es_premium()
    lista_usuarios=User.objects.filter(~Q(id=loggeado.id))
    lista_mates=[]

    for i in lista_usuarios:
        try:
            mate1=Mate.objects.get(mate=True,userEntrada=loggeado,userSalida=i)
            mate2=Mate.objects.get(mate=True,userEntrada=i,userSalida=loggeado)

            lista_mates.append(mate1.userSalida)
            lista_notificaciones.append((mate1,mate1.fecha_mate + timedelta(hours=2),"Mates"))
        except Mate.DoesNotExist:
            pass

    if(es_premium):
        matesRecibidos=Mate.objects.filter(mate=True,userSalida=loggeado)
        for mR in matesRecibidos:
            if(mR.userEntrada not in lista_mates):
                lista_notificaciones.append((mR,mR.fecha_mate + timedelta(hours=2),"Premium"))
    #lista_notificaciones.sort(key=lambda mates: mates[0].fecha_mate, reverse=True)
    return lista_notificaciones

def notificaciones_chat(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    if Usuario.objects.get(usuario = request.user).sms_validado == False:
        return redirect("registerSMS")
    user = request.user
    notificaciones_chat=[]
    chats = ChatRoom.objects.filter(participants=user)
    for chat in chats:
        con = LastConnection.objects.filter(user=user,name=chat)
        if not con:
            num = Chat.objects.filter(room = chat).count()
        elif con[0].timestamp<chat.last_message:
            num = Chat.objects.filter(room = chat,timestamp__gt=con[0].timestamp).exclude(user=user).count()
        else:
            num = 0
        if num != 0:
            if chat.group():
                notificaciones_chat.append((chat.room_name,chat.last_message,"Chat",num))
            else:
                nombre = chat.participants.all().filter(~Q(id=user.id))[0].username
                notificaciones_chat.append((nombre,chat.last_message,"Chat",num))
    #notificaciones_chat.sort(key=lambda tupla: tupla[2], reverse=True)
    return notificaciones_chat

def notificaciones(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    if Usuario.objects.get(usuario = request.user).sms_validado == False:
        return redirect("registerSMS")
    notificaciones=notificaciones_mates2(request)
    lista_chat=notificaciones_chat(request)
    notificaciones.extend(lista_chat)
    notificaciones.sort(key=lambda mates: mates[1], reverse=True)
    return notificaciones


