from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.views.generic import TemplateView
from .models import Usuario,Mates
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


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
        #us = Usuario.objects.all()
    
        registrado= Usuario.objects.filter(usuario=request.user)    
        ciudad= registrado.values('lugar')
        if(registrado.filter(piso=True)):
            us= Usuario.objects.exclude(usuario=request.user).filter(lugar__contains=ciudad).filter(piso=False)
        else:
            us= Usuario.objects.exclude(usuario=request.user).filter(lugar__contains=ciudad)
        params = {'usuarios': us}
        
        return render(request,template,params)

    return login_view(request)

def accept_mate(request):
    id_us = request.POST['id_us']

    try:
        usuario = User.objects.get(pk=id_us)
        mate, _ = Mates.objects.update_or_create(userEntrada=request.user, userSalida=usuario, defaults={'mate':True})
    except:
        response = { 'success': False }
        return JsonResponse(response)

    try:
        reverse_mate = Mates.objects.get(userEntrada=usuario, userSalida=request.user)
        mate_achieved = reverse_mate.mate
    except Mates.DoesNotExist:
        mate_achieved = False

    response = {
        'success': True,
        'mate_achieved': mate_achieved,
    }
    return JsonResponse(response)

def reject_mate(request):
    id_us = request.POST['id_us']

    try:
        usuario = User.objects.get(pk=id_us)
        mate, _ = Mates.objects.update_or_create(userEntrada=request.user, userSalida=usuario, defaults={'mate':False})
        success = True
    except:
        success = False
    response = { 'success': success }
    return JsonResponse(response)