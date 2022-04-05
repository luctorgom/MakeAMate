from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from .models import Usuario,Mate
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .recommendations import rs_score
from chat.views import crear_sala
from chat.models import Chat,ChatRoom,LastConnection

def login_view(request):
    if request.user.is_authenticated:
        return redirect(homepage)
    template='loggeos/index.html'
    if request.method == "POST":
        nameuser = request.POST['username']
        passworduser = request.POST['pass']
        user = authenticate(username=nameuser, password=passworduser)
        if user is  None:
            return render(request,template, {'no_user':True})
        else:
            login(request, user)
            return redirect(homepage)
    return render(request,template)

def logout_view(request):
    logout(request)
    return redirect(homepage)


@login_required(login_url="/login")
def homepage(request):
    if request.user.is_authenticated:
        template = 'homepage.html'

        registrado= get_object_or_404(Usuario, usuario=request.user)
        ciudad= registrado.lugar
        if(registrado.piso):
            us= Usuario.objects.exclude(usuario=request.user).filter(lugar__contains=ciudad).filter(piso=False)
        else:
            us= Usuario.objects.exclude(usuario=request.user).filter(lugar__contains=ciudad)

        lista_mates=notificaciones_mates(request)
        chats = notificaciones_chat(request)
        tags_authenticated = registrado.tags.all()
        us_sorted = sorted(us, key=lambda u: rs_score(registrado, u), reverse=True)

        tags_usuarios = {u:{tag:tag in tags_authenticated for tag in u.tags.all()} for u in us_sorted}
        
        params = {'notificaciones':lista_mates,'usuarios': tags_usuarios, 'authenticated': registrado}
        return render(request,template,params)

    return login_view(request)

def accept_mate(request):
    if not request.user.is_authenticated:
        return redirect(login_view)

    id_us = request.POST['id_us']
    usuario = get_object_or_404(User, pk=id_us)  

    if usuario == request.user:
        response = { 'success': False }
        return JsonResponse(response)

    mate, _ = Mate.objects.update_or_create(userEntrada=request.user, userSalida=usuario, defaults={'mate':True})

    # Comprueba si el mate es mutuo
    try:
        reverse_mate = Mate.objects.get(userEntrada=usuario, userSalida=request.user)
        mate_achieved = reverse_mate.mate
        crear_sala([request.user.id, usuario.id])
    except Mate.DoesNotExist:
        mate_achieved = False

    response = { 'success': True,
        'mate_achieved': mate_achieved, }

    return JsonResponse(response)

def reject_mate(request):
    if not request.user.is_authenticated:
        return redirect(login_view)

    id_us = request.POST['id_us']
    usuario = get_object_or_404(User, pk=id_us)  
    
    if usuario == request.user:
        response = { 'success': False, }
        return JsonResponse(response)
    
    mate, _ = Mate.objects.update_or_create(userEntrada=request.user, userSalida=usuario, defaults={'mate':False})
    
    response = { 'success': True, }
    return JsonResponse(response)


def payments(request):
    template='payments.html'
    return render(request,template)

def notificaciones_mates(request):
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
            lista_notificaciones.append((mate1,"Mates"))
        except Mate.DoesNotExist:
            pass

    if(es_premium):
        matesRecibidos=Mate.objects.filter(mate=True,userSalida=loggeado)
        for mR in matesRecibidos:
            if(mR.userEntrada not in lista_mates):
                lista_notificaciones.append((mR,"Premium"))
    lista_notificaciones.sort(key=lambda mates: mates[0].fecha_mate, reverse=True)
    return lista_notificaciones

def notifications_list(request):
    template='notifications.html'
    notis=notificaciones_mates(request)
    response={'notificaciones':notis}
    return render(request,template,response)

def info(request):
    return render(request,'info.html')

def notificaciones_chat(request):
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
                notificaciones_chat.append((chat.room_name,num,chat.last_message,"Chat"))
            else:
                nombre = chat.participants.all().filter(~Q(id=user.id))[0].username
                notificaciones_chat.append((nombre,num,chat.last_message,"Chat"))
    notificaciones_chat.sort(key=lambda tupla: tupla[2], reverse=True)
    return notificaciones_chat


def error_403(request,exception):
    return render(request,'error403.html')

def error_404(request,exception):
    return render(request,'error404.html')

def error_500(request,*args, **argv):
    return render(request,'error500.html',status=500)

