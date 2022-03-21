from datetime import date
from django.test import Client
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from django.contrib import auth
from .models import Aficiones, Gustos, Tags, Usuario
from django.contrib.auth.models import User


class FiltesTests(TestCase):
    
    def setUp(self):
        super().setUp()
    
    @classmethod
    def setUpTestData(cls):
        userPepe= User(username="Pepe")
        userPepe.set_password("asdfg")
        userPepe.save()

        userMaria=User(username="Maria")
        userMaria.set_password("asdfg")
        userMaria.save()

        userSara=User(username="Sara")
        userSara.set_password("asdfg")
        userSara.save()

        etiquetas= Tags.objects.create(etiqueta="No fumador")
        aficion= Aficiones.objects.create(opcionAficiones="Deportes")
        gusto= Gustos.objects.create(opcionGustos="Fotografía")
        
        Pepe= Usuario.objects.create(usuario=userPepe, piso=False, fecha_nacimiento=date(2000,12,31),
        edad=20,lugar="Sevilla")
        Maria=Usuario.objects.create(usuario=userMaria, piso=True, fecha_nacimiento=date(2000,12,30),
        edad=20,lugar="Sevilla")
        
        Sara= Usuario.objects.create(usuario=userSara, piso=True,fecha_nacimiento=date(2000,12,29)
        ,edad=20,lugar="Cádiz")
    
    

   #Nos logeamos como Pepe usuario sin Piso en Sevilla y 
   # comprobamos que solo nos sale 1 usuario, que es el que esta en la misma ciudad
    def test_filter_(self):
        c= Client()
        login= c.login(username='Pepe', password= 'asdfg')
        response=c.get('/')
        self.assertTrue( len(response.context['usuarios']) == 1)
        self.assertEqual(response.status_code, 200)
       

    #Nos logeamos como Pepe usuario sin Piso en Sevilla y 
    #comprobamos que efectivamente no salen 2 usuarios ya que uno de ellos no vive en la misma ciudad
    def test_filter_error(self):
        c= Client()
        c.login(username='Pepe', password= 'asdfg')
        response=c.get('/')
        self.assertFalse( len(response.context['usuarios']) == 2)
        self.assertEqual(response.status_code, 200)

#Test de login
class LoginTest(TestCase):
    def setUp(self):
        user = User(username='usuario')
        user.set_password('qwery')
        user.save()
        super().setUp()


    #Test de inicio de sesión con un usuario existente
    def test_login_positive(self):
        c = Client()
        response = c.post('/login/', {'username': 'usuario', 'pass': 'qwery'})
        user = auth.get_user(c)
        self.assertTrue(user.is_authenticated)
        self.assertRedirects(response, '/', status_code=302, 
        target_status_code=200, fetch_redirect_response=True)


    #Test de inicio de sesión con un usuario inexistente
    def test_login_negative(self):
        c = Client()
        response = c.post('/login/', {'username': 'inexistente', 'pass': 'inexistente'})
        user = auth.get_user(c)
        self.assertFalse(user.is_authenticated)