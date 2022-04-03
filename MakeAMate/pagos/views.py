from datetime import date, datetime
import imp
from multiprocessing import context
import re
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from principal.views import homepage, login_view
from django.views.decorators.csrf import csrf_protect
from principal.models import Usuario
from dateutil.relativedelta import relativedelta
from .models import Suscripcion
import json

@csrf_protect
def paypal(request,pk):
    if not request.user.is_authenticated:
        return redirect(login_view)
    loggeado=get_object_or_404(Usuario, usuario=request.user)
    premium=loggeado.es_premium()
    if premium:
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
    premium=loggeado.es_premium()
    if premium:
        return redirect(homepage)
    body = json.loads(request.body)
    fecha_premium = datetime.now() + relativedelta(months=1)
    date_time = fecha_premium.strftime("%m/%d/%Y, %H:%M:%S")
    Usuario.objects.update_or_create(usuario=request.user, 
    defaults={'fecha_premium': fecha_premium})
    
    return redirect(homepage)


   