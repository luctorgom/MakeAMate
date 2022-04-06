from hashlib import new
from tabnanny import check
from datetime import datetime,timedelta
from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.http import HttpResponseForbidden
from pagos.models import Suscripcion
from principal.forms import UsuarioForm, SmsForm
from .models import Aficiones, Piso, Tag, Usuario,Mate, Foto
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .recommendations import rs_score
from chat.views import crear_sala
from chat.models import Chat,ChatRoom,LastConnection
from django.db.models import Q, Count
from datetime import datetime
from django.db.models import Q
from .forms import ChangePasswordForm, ChangePhotoForm, UsuarioForm, SmsForm, UsuarioFormEdit
from principal import models
from .forms import UsuarioForm, SmsForm
import os
import secrets
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import json
from django.views.decorators.cache import never_cache
from .recommendations import rs_score
from django.contrib import messages
import ctypes


@never_cache
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
        if(registrado.tiene_piso()):
            us= Usuario.objects.exclude(usuario=request.user).filter(lugar__contains=ciudad).filter(piso=None).filter(piso_encontrado=False)
        else:
            us= Usuario.objects.exclude(usuario=request.user).filter(lugar__contains=ciudad).filter(piso_encontrado=False)

        usuarios_mate=Mate.objects.filter(userEntrada=request.user)
        set_mates={mate.userSalida.id for mate in usuarios_mate}
        usuarios_rejected=Mate.objects.filter(userSalida=request.user, mate=False)
        set_rejected={mate.userEntrada.id for mate in usuarios_rejected}

        tags_authenticated = registrado.tags.all()
        us_filtered= [u for u in us if (not u.usuario.id in set_mates) and (not u.usuario.id in set_rejected)]
        us_sorted = sorted(us_filtered, key=lambda u: rs_score(registrado, u), reverse=True)

        tags_usuarios = {u:{tag:tag in tags_authenticated for tag in u.tags.all()} for u in us_sorted}

        lista_mates=notificaciones_mates(request)
        chats = notificaciones_chat(request)
        
        params = {'notificaciones':lista_mates,'usuarios': tags_usuarios, 'authenticated': registrado}
        return render(request,template,params)

    return login_view(request)

def accept_mate(request):
    if not request.user.is_authenticated:
        return redirect(login_view)

    id_us = request.POST['id_us']
    usuario = get_object_or_404(User, pk=id_us)
    
    perfil_usuario = get_object_or_404(Usuario, usuario=usuario)
    perfil_logeado = get_object_or_404(Usuario, usuario=request.user)

    misma_ciudad = perfil_usuario.lugar == perfil_logeado.lugar
    tienen_piso = perfil_usuario.tiene_piso() and perfil_logeado.tiene_piso()
    is_rejected = Mate.objects.filter(userEntrada=usuario,userSalida=request.user,mate=False).exists()
    has_mated = Mate.objects.filter(userEntrada=request.user,userSalida=usuario).exists()

    if usuario == request.user or not misma_ciudad or is_rejected or has_mated or tienen_piso:
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
    
    perfil_usuario = get_object_or_404(Usuario, usuario=usuario)
    perfil_logeado = get_object_or_404(Usuario, usuario=request.user)

    misma_ciudad = perfil_usuario.lugar == perfil_logeado.lugar
    tienen_piso = perfil_usuario.tiene_piso() and perfil_logeado.tiene_piso()
    is_rejected = Mate.objects.filter(userEntrada=usuario,userSalida=request.user,mate=False).exists()
    has_mated = Mate.objects.filter(userEntrada=request.user,userSalida=usuario).exists()

    if usuario == request.user or not misma_ciudad or is_rejected or has_mated or tienen_piso:
        response = { 'success': False, }
        return JsonResponse(response)
    
    mate, _ = Mate.objects.update_or_create(userEntrada=request.user, userSalida=usuario, defaults={'mate':False})
    response = { 'success': True, }
    return JsonResponse(response)


def payments(request):
    if not request.user.is_authenticated:
        return redirect(login_view) 

    template='payments.html'
    loggeado=get_object_or_404(Usuario, usuario=request.user)
    premium= loggeado.es_premium()
    lista_mates=notificaciones_mates(request)

    try :
        suscripcion=Suscripcion.objects.all()[0]  
        params={'notificaciones':lista_mates,'suscripcion':suscripcion, 'premium':premium,'hay_suscripciones':True}  
        return render(request,template,params) 
    except:
        params={'notificaciones':lista_mates,'premium':premium,'hay_suscripciones':False}
        return render(request,template,params) 

    

def terminos(request):
    template='loggeos/terminos_1.html'
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
    lista_mates=notificaciones_mates(request)

    return render(request,'info.html',{'notificaciones':lista_mates})

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
    return render(request,'error403.html', status=403)

def error_404(request,exception):
    return render(request,'error404.html', status=404)

def error_500(request,*args, **argv):
    return render(request,'error500.html',status=500)


def estadisticas_mates(request):
    loggeado= request.user
    perfil=Usuario.objects.get(usuario=loggeado)
    es_premium= perfil.es_premium()
    lista_mates=notificaciones_mates(request)

    if(es_premium):
        #NUMERO DE INTERACIONES
        interacciones=Mate.objects.filter(userSalida=loggeado).count()
        
        #QUIEN TE HA DADO LIKE EN EL ÚLTIMO MES
        mesActual=datetime.now().month
        listmates=[]
        matesRecibidos=Mate.objects.filter(mate=True,userSalida=loggeado, fecha_mate__month=mesActual)
        for mR in matesRecibidos:
            listmates.append(mR.userEntrada)
        matesDados=Mate.objects.filter(userEntrada=loggeado)
        eliminados=0
        for mD in matesDados:
            #print(mD.userSalida)
            if(mD.userSalida in listmates):
                eliminados+=1
                listmates.remove(mD.userSalida)
        listperfiles=[]
        for us in listmates:
            listperfiles.append(Usuario.objects.get(usuario=us))

        #INTERACCIONES POR DÍA PARA LA GRÁFICA
        matesporFecha=matesRecibidos.values('fecha_mate__date').annotate(dcount=Count('fecha_mate__date')).order_by()
        listFecha=[]
        listdcount=[]
        for i in range(0,matesporFecha.count()):
            listFecha.append(matesporFecha[i]['fecha_mate__date'].strftime("%d/%m/%Y"))
            listdcount.append(matesporFecha[i]['dcount'])
        dictGrafica=dict(zip(listFecha,listdcount))
        
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
        sorted_tuples = sorted(dicTags.items(), key=lambda item: item[1], reverse=True)
        sortedTags = {k: v for k, v in sorted_tuples}

        #COMPARATIVA NO PREMIUM VS PREMIUM
        fechaInicioPremium=perfil.fecha_premium - timedelta(days=30)
        mRNoPremium=Mate.objects.filter(mate=True,userSalida=loggeado, fecha_mate__lt=fechaInicioPremium).count()
        mRPremium=Mate.objects.filter(mate=True,userSalida=loggeado, fecha_mate__gt=fechaInicioPremium).count()

        #SCORE CON LAS PERSONAS QUE TE HAN DADO LIKE
        listScore=[]
        for i in listmates:
            perfilU=Usuario.objects.get(usuario=i)
            score = rs_score(perfil,perfilU)
            listScore.append(round(score*100) if(score*100 < 100)  else 100)
        dictScore=dict(zip(listmates,listScore))

        params={"notificaciones":lista_mates,"interacciones":interacciones,"lista":listperfiles, "topTags":sortedTags, "matesGrafica":dictGrafica, "matesNPremium":mRNoPremium,
                "matesPremium":mRPremium, "scoreLikes":dictScore}
        return render(request,'estadisticas.html',params)
    else:
        return payments(request)

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
            form_tags = form.cleaned_data['tags']
            form_aficiones = form.cleaned_data['aficiones']
            form_zona_piso = form.cleaned_data['zona_piso']
            form_telefono_usuario = form.cleaned_data['telefono_usuario']        
            

            user = User.objects.create(username=form_usuario,first_name=form_nombre,
            last_name=form_apellidos, email=form_correo)
            user.set_password(form_password)
            user.save()


            if form_zona_piso != "":
                piso = Piso.objects.create(zona = form_zona_piso)
                perfil = Usuario.objects.create(usuario = user, piso = piso,
                fecha_nacimiento = form_fecha_nacimiento, lugar = form_lugar, nacionalidad = form_nacionalidad,
                genero = form_genero,foto = form_foto,telefono=form_telefono_usuario)
            else:
                perfil = Usuario.objects.create(usuario = user, 
                fecha_nacimiento = form_fecha_nacimiento, lugar = form_lugar, nacionalidad = form_nacionalidad,
                genero = form_genero, foto = form_foto, telefono=form_telefono_usuario) 

            perfil.tags.set(form_tags)
            perfil.aficiones.set(form_aficiones)
            perfil.save()
            return redirect('registerSMS/'+str(user.id), {'user_id': user.id})

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
                    perfil.save()
                    messages.success(request, message="Código validado correctamente. El usuario ha sido creado.")
                else:
                    messages.error(request, message="El código es incorrecto. Inténtelo de nuevo.")
        except TwilioRestException as e:
            # TODO: Cuando se hacen 5 llamadas a la API con el mismo telefono en menos de 10 min peta y lanza TwilioRestException.
            # Comprobar documentación al respecto: https://www.twilio.com/docs/api/errors/60203
            messages.error(request, message="TwilioRestException. Error validando el código: {}".format(e))
        return render(request, 'loggeos/index.html', {'form': form})


    verification = start_verification(telefono)
    form = SmsForm()
    if request.method == 'POST':
        form = SmsForm(request.POST, request.FILES)
        if form.is_valid():
            codigo = form.cleaned_data["codigo"]
            return check_verification(telefono, codigo, verification)

    return render(request, 'loggeos/registerSMS.html', {'form': form})

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect(homepage)

    user = request.user
    usuario = Usuario.objects.get(usuario = user)
    lista_mates=notificaciones_mates(request)

    initial_dict = {
        'foto_usuario': usuario.foto,
        'lugar': usuario.lugar,
        'genero': usuario.genero,
        'zona_piso': usuario.piso.zona if (usuario.piso)  else "",
        'descripcion': usuario.descripcion,
        'piso_encontrado': usuario.piso_encontrado,
        # 'idiomas': usuario.idiomas.all(),
        'tags': usuario.tags.all(), 
        'aficiones': usuario.aficiones.all()
    }

    form_change_password = ChangePasswordForm()
    form_change_photo = ChangePhotoForm()
    form = UsuarioFormEdit(initial = initial_dict)
    if request.method == 'POST':
        if "actualizarPerfil" in request.POST:
            form_change_password = ChangePasswordForm(request.POST)
            form = UsuarioFormEdit(request.POST)
            form_change_photo = ChangePhotoForm(request.POST, request.FILES)
            if form.is_valid():
                form_lugar = form.cleaned_data['lugar']
                form_genero = form.cleaned_data['genero']
                form_zona_piso = form.cleaned_data['zona_piso']
                form_descripcion = form.cleaned_data['descripcion']
                form_piso_encontrado = form.cleaned_data['piso_encontrado']

                # form_idiomas = form.cleaned_data['idiomas']
                form_tags = form.cleaned_data['tags']
                form_aficiones = form.cleaned_data['aficiones']

                user_actual = request.user
                perfil = Usuario.objects.get(usuario = user_actual)
                if form_zona_piso != "":
                    piso_usuario, no_existe = Piso.objects.get_or_create(zona = form_zona_piso)
                    if no_existe:
                        piso_usuario.save()
                    Usuario.objects.filter(usuario = user_actual).update(lugar = form_lugar, descripcion = form_descripcion,
                    genero = form_genero, piso_encontrado = form_piso_encontrado,
                    piso = piso_usuario)
                else:
                    Usuario.objects.filter(usuario = user_actual).update(piso = None, lugar = form_lugar, descripcion = form_descripcion,
                        genero = form_genero, piso_encontrado = form_piso_encontrado)

                perfil_updated_2 = Usuario.objects.get(usuario = user_actual)
                # perfil_updated_2.idiomas.set(form_idiomas)
                perfil_updated_2.tags.set(form_tags)
                perfil_updated_2.aficiones.set(form_aficiones)
                perfil_updated_2.save() 
                return redirect("/profile") 
            else:
                form_change_password = ChangePasswordForm()
                form_change_photo = ChangePhotoForm()
                return render(request, 'profile.html', {'notificaciones':lista_mates,'form': form, 'form_change_password':form_change_password,
                'form_change_photo': form_change_photo,'piso_encontrado':usuario.piso_encontrado})

        if "actualizarContraseña" in request.POST:
            form_change_password = ChangePasswordForm(request.POST)
            form = UsuarioFormEdit(request.POST)
            form_change_photo = ChangePhotoForm(request.POST, request.FILES)
            if form_change_password.is_valid():
                form_password = form_change_password.cleaned_data['password']
                usuario = request.user
                usuario.set_password(form_password)
                usuario.save()
                return redirect("/profile") 
            else:
                form_change_photo = ChangePhotoForm()
                form = UsuarioFormEdit(initial = initial_dict)
                return render(request, 'profile.html', {'notificaciones':lista_mates,'form': form, 'form_change_password':form_change_password,
                'form_change_photo': form_change_photo,'usuario':usuario})
        
        if "actualizarFoto" in request.POST:
            form_change_password = ChangePasswordForm(request.POST)
            form = UsuarioFormEdit(request.POST)
            form_change_photo = ChangePhotoForm(request.POST, request.FILES)
            if form_change_photo.is_valid(): 
                form_photo = form_change_photo.cleaned_data['foto_usuario']
                user = request.user

                Usuario.objects.filter(usuario=user.id).update(foto=form_photo)
 
                return redirect("/profile")
            else:
                form = UsuarioFormEdit(initial = initial_dict)
                return render(request, 'profile.html', {'notificaciones':lista_mates,'form': form, 'form_change_password':form_change_password,
                'form_change_photo': form_change_photo,'usuario':usuario})


    return render(request, 'profile.html', {'notificaciones':lista_mates,'form': form, 'form_change_password':form_change_password,
            'form_change_photo': form_change_photo})



