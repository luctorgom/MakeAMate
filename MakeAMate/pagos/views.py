from datetime import date, datetime,timedelta
from django.utils import timezone
import imp
from multiprocessing import context
import re
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse

from django.views.decorators.csrf import csrf_protect
from principal.models import Usuario
from dateutil.relativedelta import relativedelta
from .models import Suscripcion
from django.utils.timezone import make_aware
import json
from django.contrib.auth.models import User
from principal.models import Mate, Usuario
from django.db.models import Q
from chat.models import Chat,ChatRoom,LastConnection

@csrf_protect
def paypal(request,pk):
    if not request.user.is_authenticated:
        return redirect("login")
    elif Usuario.objects.get(usuario = request.user).sms_validado == False:
        return redirect("registerSMS")
    else:
        loggeado=get_object_or_404(Usuario, usuario=request.user)
        premium=loggeado.es_premium()
        if premium:
            return redirect("/")
        template_name='pagos.html'
        suscripcion= get_object_or_404(Suscripcion, id=pk)
        context={'notificaciones':notificaciones(request),'suscripcion': suscripcion,'usuario':loggeado}
        return render(request, template_name, context)

@csrf_protect
def paymentComplete(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    elif Usuario.objects.get(usuario = request.user).sms_validado == False:
        return redirect("registerSMS")
    else:
        loggeado=get_object_or_404(Usuario, usuario=request.user)
        premium=loggeado.es_premium()
        if premium:
            return redirect("/login")
        fecha_premium = timezone.now() + relativedelta(months=1)
        loggeado.fecha_premium=fecha_premium
        loggeado.save()
        return redirect("/login")


def notificaciones_mates(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    elif Usuario.objects.get(usuario = request.user).sms_validado == False:
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
    elif Usuario.objects.get(usuario = request.user).sms_validado == False:
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
    elif Usuario.objects.get(usuario = request.user).sms_validado == False:
        return redirect("registerSMS")
    notificaciones=notificaciones_mates(request)
    lista_chat=notificaciones_chat(request)
    notificaciones.extend(lista_chat)
    notificaciones.sort(key=lambda mates: mates[1], reverse=True)
    return notificaciones

