from asyncio.windows_events import NULL
from django.test import Client, TestCase
from django.contrib.auth.models import User
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from principal.models import Usuario
from pagos.models import Suscripcion
from django.utils.timezone import make_aware

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
        Maria=Usuario.objects.create(usuario=userMaria, fecha_nacimiento=date(2000,12,30),lugar="Sevilla", fecha_premium=aware_fecha_premium)
        self.Pepe= Usuario.objects.create(usuario=userPepe, fecha_nacimiento=date(2000,12,31),lugar="Sevilla")
        self.plan_premium=Suscripcion.objects.create(name="Plan Premium", price=4.99, description="!Consigue un boost en tu perfil y además averigua quien ve tu perfil!")
        self.plan_premium.save()
       

    #Con este test comprobamos que un usuario logeado puede comprar un suscripción
    # def testPayments(self):
    #     c= Client()
    #     c.login(username='Pepe', password= 'asdfg')
    #     response=c.get("/payments/")
    #     suscripcion=response.context['suscripcion']
    #     self.assertEqual(suscripcion.name,"Plan Premium")
    #     self.assertEqual(response.status_code, 200)
    
    #Comprobamos que un usuario deslogegado no puede acceder a la tienda
    # def testPaymentsLogoutUser(self):
    #     c= Client()
    #     response=c.get("/payments/")
    #     self.assertRedirects(response, "/login/")

    # def testPaypal(self):
    #     c= Client()
    #     c.login(username='Pepe', password= 'asdfg')
    #     response=c.get("paypal/", pk=self.plan_premium.id)
    #     self.assertEqual(response.status_code, 200)

    def testPaymentCompleteUserNotLogin(self):
        c= Client()
        response=c.get("/pagos/complete/")
        self.assertRedirects(response, "/login/")
    
    def testPaymentCompleteUserAlreadyPremium(self):
        c= Client()
        c.login(username='Maria', password= 'asdfg')
        response=c.get("/pagos/complete/")
        self.assertRedirects(response, "/")

    def testPaymentComplete(self):
        c= Client()
        c.login(username='Pepe', password= 'asdfg')
        response=c.get("/pagos/complete/")
        print(self.Pepe.fecha_premium)
       



