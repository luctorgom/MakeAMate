from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.views.generic import TemplateView
from .models import Usuario


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

def homepage(request):
    if request.user.is_authenticated:
        template = 'homepage.html'
        us = Usuario.objects.all()
        print(us)
        params = {'usuarios': us}
        
        return render(request,template,params)

    return login_view(request)