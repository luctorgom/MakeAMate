from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from .models import Usuario,Mates
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

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

    mate, _ = Mates.objects.update_or_create(userEntrada=request.user, userSalida=usuario, defaults={'mate':True})

    # Comprueba si el mate es mutuo
    try:
        reverse_mate = Mates.objects.get(userEntrada=usuario, userSalida=request.user)
        mate_achieved = reverse_mate.mate
    except Mates.DoesNotExist:
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
    
    mate, _ = Mates.objects.update_or_create(userEntrada=request.user, userSalida=usuario, defaults={'mate':False})
    
    response = { 'success': True, }
    return JsonResponse(response)


def payments(request):
    template='payments.html'
    return render(request,template) 

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
