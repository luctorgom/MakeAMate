from django.test import Client, TestCase
from django.contrib.auth.models import User
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from principal.models import Usuario
from pagos.models import Suscripcion
from django.utils.timezone import make_aware
from django.urls import reverse, resolve

class PaymentsTest(TestCase):
    
    def setUp(self):
        super().setUp()
        userPepe= User(username="Pepe")
        userPepe.set_password("asdfg")
        userPepe.save()

        userMaria=User(username="Maria")
        userMaria.set_password("asdfg")
        userMaria.save()
        fecha_premium=datetime(2022,9,22,0,0,0,0)
        aware_fecha_premium=make_aware(fecha_premium)
        
        tfn1 = "+34666777111"
        tfn2 = "+34666777222"
        
        Maria=Usuario.objects.create(usuario=userMaria, fecha_nacimiento=date(2000,12,30),lugar="Sevilla", fecha_premium=aware_fecha_premium, telefono=tfn1, sms_validado=True)
        self.Pepe= Usuario.objects.create(usuario=userPepe, fecha_nacimiento=date(2000,12,31),lugar="Sevilla", telefono=tfn2, sms_validado=True)
        
        self.plan_premium=Suscripcion.objects.create(id=1,name="Plan Premium", price=4.99, description="!Consigue un boost en tu perfil y además averigua quien ve tu perfil!")
        self.plan_premium.save()
       

    #Con este test comprobamos que un usuario logeado puede comprar un suscripción
    
    def test_payments(self):
        c= Client()
        c.login(username='Pepe', password= 'asdfg')
        response=c.get("/payments/")
        suscripcion=response.context['suscripcion']
        self.assertEqual(suscripcion.name,"Plan Premium")
        self.assertEqual(response.status_code, 200)
    
    #Comprobamos que un usuario deslogegado no puede acceder a la tienda
    
    def test_payments_logout_user(self):
        c= Client()
        response=c.get("/payments/")
        self.assertRedirects(response, "/login/")

    #Comprobamos que se puede comprar la suscripción
    
    def test_paypal(self):
        c= Client()
        c.login(username='Pepe', password= 'asdfg')        
        response=c.get("/paypal/1/")
        suscripcion=response.context['suscripcion']
        self.assertEqual(suscripcion.name,"Plan Premium")
        self.assertEqual(response.status_code, 200)
       
        
    
    #Comprobamos que un usuario deslogegado no puede comprar una suscripción

    def test_paypal_user_not_login(self):
        c= Client()       
        response=c.get("/paypal/1/")
        self.assertRedirects(response, "/login/")
    
    #Comprobamos que un usuario que ya es premium no puede comprar una suscripción
    
    def test_paypal_user_already_premium(self):
        c= Client() 
        c.login(username='Maria', password= 'asdfg')      
        response=c.get("/paypal/1/")
        self.assertRedirects(response, "/")
   
   #Comprobamos que un usuario deslogegado no puede finalizar una transacción y setear una fecha final de premium
    def test_payment_complete_user_not_login(self):
        c= Client()
        response=c.get("/pagos/complete/")
        self.assertEquals(response.status_code, 404)
    
    #Comprobamos que un usuario que ya es premium no finalizar una transacción y setear una fecha final de premium
    def test_payment_complete_user_already_premium(self):
        c= Client()
        c.login(username='Maria', password= 'asdfg')
        response=c.get("/pagos/complete/")
        self.assertEquals(response.status_code, 404)

    #Comprobamos que el usuario Pepe sin fecha premium al hacer la compra del plan premium tiene una fecha final de
    #su plan premium
    
    def test_payment_complete(self):
        c= Client()
        c.login(username='Pepe', password= 'asdfg')
        response=c.get("/pagos/complete/")
        self.assertFalse(self.Pepe.fecha_premium, None)
