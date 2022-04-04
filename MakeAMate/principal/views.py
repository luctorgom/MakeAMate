from tabnanny import check
from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from principal.forms import UsuarioForm, SmsForm
from .models import Aficiones, Idioma, Piso, Tag, Usuario,Mate, Foto
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from datetime import datetime
from django.db.models import Q

from .forms import UsuarioForm, SmsForm
import os
import secrets
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import json
from django.contrib import messages
import ctypes


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


def register_view(request):
    template='loggeos/register2.html'    
    params = {'form': UsuarioForm()}
    return render(request,template, params)


@login_required(login_url="/login")
def homepage(request):
    if request.user.is_authenticated:
        if Usuario.objects.get(usuario = request.user).sms_validado == False:
            return render(request, 'loggeos/registerSMS.html', {'form': SmsForm})
        template = 'homepage.html'

        registrado= get_object_or_404(Usuario, usuario=request.user)
        ciudad= registrado.lugar
        if(registrado.piso):
            us= Usuario.objects.exclude(usuario=request.user).filter(lugar__contains=ciudad).filter(piso=False)
        else:
            us= Usuario.objects.exclude(usuario=request.user).filter(lugar__contains=ciudad)

        lista_mates=notificaciones_mates(request)
        tags_authenticated = registrado.tags.all()
        tags_usuarios = {u:{tag:tag in tags_authenticated for tag in u.tags.all()} for u in us}
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

def terminos(request):
    template='loggeos/terminos_1.html'
    return render(request,template) 

def prueba(request):
    form = SmsForm()
    template='loggeos/registerSMS.html'
    return render(request,template,{'form': form}) 

def notificaciones_mates(request):
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

def estadisticas_mates(request):
    loggeado= request.user
    perfil=Usuario.objects.get(usuario=loggeado)

    #QUIEN TE HA DADO LIKE EN EL ÚLTIMO MES
    mesActual=datetime.now().month
    listmates=[]
    matesRecibidos=Mate.objects.filter(mate=True,userSalida=loggeado, fecha_mate__month=mesActual)
    #print(matesRecibidos)
    for mR in matesRecibidos:
        listmates.append(mR.userEntrada)
    #print(listmates)
    matesDados=Mate.objects.filter(userEntrada=loggeado)
    #print(matesDados)
    eliminados=0
    for mD in matesDados:
        #print(mD.userSalida)
        if(mD.userSalida in listmates):
            eliminados+=1
            listmates.remove(mD.userSalida)
            #print(listmates)

    #LIKES POR DÍA PARA LA GRÁFICA
    matesporFecha=matesRecibidos.values('fecha_mate__date').annotate(dcount=Count('fecha_mate__date')-eliminados).order_by()
    #print(matesporFecha[0]['fecha_mate__date']) Recorrer diccionario par dia-numero likes

    #TOP TAGS CON QUIEN TE HA DADO LIKE
    listtags=[]
    tagsloggeado=perfil.tags.all().values()
    for tagl in tagsloggeado:
        listtags.append(tagl['etiqueta'])

    listTop=[]
    for m in listmates:
        tagsMates=Usuario.objects.get(usuario=m).tags.all().values()
        for tm in tagsMates:
            if tm['etiqueta'] in listtags:
                listTop.append(tm['etiqueta'])
    dicTags=dict(zip(listTop,map(lambda x: listTop.count(x),listTop)))

    #COMPARATIVA NO PREMIUM VS PREMIUM
    fechaPremium=perfil.fecha_premium
    #mRNoPremium=Mates.objects.filter(mate=True,userSalida=loggeado, fecha_mate__lt=fechaPremium).count
    #mRPremium=Mates.objects.filter(mate=True,userSalida=loggeado, fecha_mate__gt=fechaPremium).count

    params={"lista":listmates, "topTags":dicTags}
    return render(request,'homepage.html',params)

def registro(request):
    if request.user.is_authenticated:
        return redirect(homepage)
    form = UsuarioForm()
    if request.method == 'POST':
        form = UsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            form_usuario = form.cleaned_data["username"]
            form_password = form.cleaned_data['password']
            form_nombre = form.cleaned_data['nombre']
            form_apellidos = form.cleaned_data['apellidos']
            form_correo = form.cleaned_data['correo']

            form_foto = form.cleaned_data['foto_usuario']
            form_fecha_nacimiento = form.cleaned_data['fecha_nacimiento']
            form_lugar = form.cleaned_data['lugar']
            form_nacionalidad = form.cleaned_data['nacionalidad']
            form_genero = form.cleaned_data['genero']
           # form_idiomas = form.cleaned_data['idiomas']
            form_tags = form.cleaned_data['tags']
            form_aficiones = form.cleaned_data['aficiones']
            form_zona_piso = form.cleaned_data['zona_piso']
            form_telefono_usuario = form.cleaned_data['telefono_usuario']         
            

            user = User.objects.create(username=form_usuario,first_name=form_nombre,
            last_name=form_apellidos, email=form_correo)
            user.set_password(form_password)

            if form_zona_piso != None:
                piso = Piso.objects.create(zona = form_zona_piso)
                perfil = Usuario.objects.create(usuario = user, piso = piso,
                fecha_nacimiento = form_fecha_nacimiento, lugar = form_lugar, nacionalidad = form_nacionalidad,
                genero = form_genero,foto = form_foto,telefono=form_telefono_usuario)
            else:
                perfil = Usuario.objects.create(usuario = user, 
                fecha_nacimiento = form_fecha_nacimiento, lugar = form_lugar, nacionalidad = form_nacionalidad,
                genero = form_genero, foto = form_foto, telefono=form_telefono_usuario) 

           # perfil.idiomas.set(form_idiomas)
            perfil.tags.set(form_tags)
            perfil.aficiones.set(form_aficiones)
            return redirect('registerSMS/'+str(user.id), {'user_id': user.id})
            #return redirect('registerSMS/'+str(user.id), {'user_id': user.id})

    return render(request, 'loggeos/register2.html', {'form': form})


def twilio(request, user_id):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)
    servicio = "VAfd6998ee6818ae4ec6d0344f5a25c96d"
    user = User.objects.get(id = user_id)
    perfil = Usuario.objects.get(usuario = user)
    piso = perfil.piso
    telefono = perfil.telefono

    def start_verification(telefono):
        try:
            verification = client.verify \
                .services(servicio) \
                .verifications \
                .create(to=telefono, channel="sms")
            return verification
        except TwilioRestException as e:
            messages.error(request, message="TwilioRestException. Error validando el código: {}".format(e))
        

    def check_verification(telefono, codigo, verification):
        try:
            if(verification.status=="pending"):
    
                verification_check = client.verify \
                                    .services(servicio) \
                                    .verification_checks \
                                    .create(to=telefono, code=codigo)
                if verification_check.status=="approved":                 
                    perfil.sms_validado = True
                    messages.success(request, message="Código validado correctamente. El usuario ha sido creado.")
                else:
                    messages.error(request, message="El código es incorrecto. Inténtelo de nuevo.")
        except TwilioRestException as e:
            # TODO: Cuando se hacen 5 llamadas a la API con el mismo telefono en menos de 10 min peta y lanza TwilioRestException.
            # Comprobar documentación al respecto: https://www.twilio.com/docs/api/errors/60203
            messages.error(request, message="TwilioRestException. Error validando el código: {}".format(e))

        return render(request, 'homepage.html', {'form': form})

    verification = start_verification(telefono)
    form = SmsForm()
    if request.method == 'POST':
        form = SmsForm(request.POST, request.FILES)
        if form.is_valid():
            codigo = form.cleaned_data["codigo"]
            return check_verification(telefono, codigo, verification)

    return render(request, 'loggeos/registerSMS.html', {'form': form})