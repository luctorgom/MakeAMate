from datetime import date
from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.contrib import auth
from principal.models import Aficiones, Gustos, Tags

from principal.models import Mates, Usuario

class NotificacionesTest(TestCase):
    def setUp(self):
        user = User(username='usuario')
        user.set_password('qwery')
        user.save()

        user2 = User(username='usuario2')
        user2.set_password('qwery')
        user2.save()

        user3 = User(username='usuario3')
        user3.set_password('qwery')
        user3.save()


        pepe= Usuario.objects.create(usuario=user, piso=False, fecha_nacimiento=date(2000,12,31),
        edad=20,lugar="Sevilla")
        maria=Usuario.objects.create(usuario=user2, piso=True, fecha_nacimiento=date(2000,12,30),
        edad=20,lugar="Sevilla")
        
        sara= Usuario.objects.create(usuario=user3, piso=True,fecha_nacimiento=date(2000,12,29)
        ,edad=20,lugar="Cádiz")

        #MATE ENTRE user y user2
        mate1 = Mates.objects.create(mate=True,userEntrada=user, userSalida=user2)
        mate2 = Mates.objects.create(mate=True,userEntrada=user2, userSalida=user)

        #EL user LE DA MATE AL user3, PERO EL user3 NO LE DA MATE A ÉL
        mate3 = Mates.objects.create(mate=True,userEntrada=user, userSalida=user3)
        super().setUp()


    #El usuario "user" tiene un mate, por lo que su lista de mates será de tamaño 1
    def test_notificaciones(self):
        c = Client()
        response_user = c.post('/login/', {'username': 'usuario', 'pass': 'qwery'})
        response2 = c.get('/')
        lista_mates = response2.context['notificaciones']

        self.assertTrue(len(lista_mates) == 1)

    #El usuario "user3" no tiene ningún mate, por lo que su lista de mates será de tamaño 0
    def test_notificaciones_2(self):
        c = Client()
        response = c.post('/login/', {'username': 'usuario3', 'pass': 'qwery'})
        response2 = c.get('/')
        lista_mates = response2.context['notificaciones']
        self.assertTrue(len(lista_mates) == 0)