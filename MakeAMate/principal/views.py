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

        usuarios_mate=Mate.objects.filter(userEntrada=request.user)
        set_mates={mate.userSalida.id for mate in usuarios_mate}
        usuarios_rejected=Mate.objects.filter(userSalida=request.user, mate=False)
        set_rejected={mate.userEntrada.id for mate in usuarios_rejected}

        tags_authenticated = registrado.tags.all()
        us_filtered= [u for u in us if (not u.usuario.id in set_mates) and (not u.usuario.id in set_rejected)]
        us_sorted = sorted(us_filtered, key=lambda u: rs_score(registrado, u), reverse=True)

        tags_usuarios = {u:{tag:tag in tags_authenticated for tag in u.tags.all()} for u in us_sorted}

        lista_mates=notificaciones_mates(request)
        
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