from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.generic import TemplateView


def login_view(request):
    if request.user.is_authenticated:
        return redirect(base)
    template='loggeos/index.html'
    if request.method == "POST":
        nameuser = request.POST['username']
        passworduser = request.POST['pass']
        user = authenticate(username=nameuser, password=passworduser)
        if user is  None:    
            return render(request,template, {'no_user':True})
        else:    
            login(request, user)
            return redirect(base)  
    return render(request,template)

def logout_view(request):
    logout(request)
    return redirect(base)


def homepage(request):
    return render(request, 'homepage.html')


def base(request):
    if request.user.is_authenticated:
        return render(request, 'base.html')
    return login_view(request)