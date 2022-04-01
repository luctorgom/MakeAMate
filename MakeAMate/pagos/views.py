from datetime import date, datetime
import imp
from multiprocessing import context
import re
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from principal.views import homepage, login_view
from django.views.decorators.csrf import csrf_protect
from principal.models import Usuario

from .models import Suscripcion
import json

@csrf_protect
def paypal(request,pk):
    if not request.user.is_authenticated:
        return redirect(login_view)
    loggeado=get_object_or_404(Usuario, usuario=request.user)
    if loggeado.is_premium():
        return redirect(homepage)
    template_name='pagos/pagos.html'
    suscripcion= Suscripcion.objects.get(id=pk)
    context={'suscripcion': suscripcion}
    return render(request, template_name, context)

@csrf_protect
def paymentComplete(request):
    if not request.user.is_authenticated:
        return redirect(login_view)
    loggeado=get_object_or_404(Usuario, usuario=request.user)  
    if loggeado.is_premium():
        return redirect(homepage)
    body = json.loads(request.body)
    print('BODY:', body)
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    Usuario.objects.update_or_create(usuario=request.user, 
    defaults={'fecha_premium': now})
    
    return JsonResponse('Payment completed!', safe=False)


   