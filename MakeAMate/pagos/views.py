import imp
from multiprocessing import context
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from principal.models import Usuario

from .models import Order, Suscripcion
import json


def paypal(request,pk):
    template_name='pagos/pagos.html'
    suscripcion= Suscripcion.objects.get(id=pk)
    context={'suscripcion': suscripcion}
    return render(request, template_name, context)

def paymentComplete(request):
    
    print(Usuario.objects.get(request.user))
    body = json.loads(request.body)
    print('BODY:', body)
    suscripcion = Suscripcion.objects.get(id=body['suscripcionId'])
    Order.objects.create(
        suscripcion=suscripcion
        )
    print(Order)
    return JsonResponse('Payment completed!', safe=False)


   