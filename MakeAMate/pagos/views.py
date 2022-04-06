from datetime import date, datetime
from django.utils import timezone
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
from django.utils.timezone import make_aware
import json
from django.contrib.auth.models import User
from principal.models import Mate, Usuario
from django.db.models import Q

@csrf_protect
def paypal(request,pk):
    lista_mates = notificaciones_mates(request)

    if not request.user.is_authenticated:
        return redirect(login_view)
    loggeado=get_object_or_404(Usuario, usuario=request.user)
    premium=loggeado.es_premium()
    if premium:
        return redirect(homepage)
    template_name='pagos.html'
    suscripcion= get_object_or_404(Suscripcion, id=pk)
    context={'notificaciones':lista_mates,'suscripcion': suscripcion}
    return render(request, template_name, context)

@csrf_protect
def paymentComplete(request):
    if not request.user.is_authenticated:
        return redirect(login_view)
    loggeado=get_object_or_404(Usuario, usuario=request.user)
    premium=loggeado.es_premium()
    if premium:
        return redirect(homepage)
    fecha_premium = timezone.now() + relativedelta(months=1)
    loggeado.fecha_premium=fecha_premium
    loggeado.save()
    return redirect(homepage)

def homepageRedirect(request,pk):
    return redirect(homepage)

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

