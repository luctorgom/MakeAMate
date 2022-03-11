from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm

def notification_view(request):
    template='notificacion.html'
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
    else:
        form = AuthenticationForm()
    return render(request,template,{'form':form})