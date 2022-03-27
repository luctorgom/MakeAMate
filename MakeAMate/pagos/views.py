from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

def paypal(request):
    return render(request, template_name='pagos/pagos.html')
   