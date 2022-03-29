from datetime import date, datetime
import imp
from multiprocessing import context
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from principal.models import Usuario

from .models import Suscripcion
import json


def paypal(request,pk):
    template_name='pagos/pagos.html'
    suscripcion= Suscripcion.objects.get(id=pk)
    context={'suscripcion': suscripcion}
    return render(request, template_name, context)


def paymentComplete(request):
    
    body = json.loads(request.body)
    print('BODY:', body)
    now = datetime.now()
        
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    Usuario.objects.update_or_create(usuario=request.user, 
    defaults={'fecha_premium': now})
    registrado=Usuario.objects.get(usuario=request.user)
    return JsonResponse('Payment completed!', safe=False)


   