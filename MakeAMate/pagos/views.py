from datetime import date, datetime
import imp
from multiprocessing import context
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from principal.views import login_view
from django.views.decorators.csrf import csrf_protect
from principal.models import Usuario

from .models import Suscripcion
import json

@csrf_protect
def paypal(request,pk):
    if not request.user.is_authenticated:
        return redirect(login_view)
    template_name='pagos/pagos.html'
    suscripcion= Suscripcion.objects.get(id=pk)
    context={'suscripcion': suscripcion}
    return render(request, template_name, context)

@csrf_protect
def paymentComplete(request):
    if not request.user.is_authenticated:
        return redirect(login_view)
    
    body = json.loads(request.body)
    print('BODY:', body)
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    Usuario.objects.update_or_create(usuario=request.user, 
    defaults={'fecha_premium': now})
    
    return JsonResponse('Payment completed!', safe=False)


   