from datetime import date
import json
from django.test import Client, TestCase
from django.conf import settings
from django.contrib import auth
from .models import Aficiones, Gustos, Mates, Tags, Usuario
from django.contrib.auth.models import User

# Test mates
class MateTestCase(TestCase):
    def setUp(self):
        # Modificar si se borra el campo edad...
        self.user1 = User(id=0,username="us1")
        self.user1.set_password('123')
        self.user2 = User(id=1,username="us2")
        self.user2.set_password('123')
        self.user3 = User(id=2,username="us3")
        self.user3.set_password('123')

        perfil1 = Usuario(usuario=self.user1,piso=True,fecha_nacimiento="2000-1-1",edad=1,lugar="Sevilla",nacionalidad="Española",
                            genero='F',pronombres="Ella",idiomas="ES",universidad="US",estudios="Informática")
        perfil2 = Usuario(usuario=self.user2,piso=True,fecha_nacimiento="2000-1-1",edad=1,lugar="Sevilla",nacionalidad="Española",
                            genero='F',pronombres="Ella",idiomas="ES",universidad="US",estudios="Informática")
        perfil3 = Usuario(usuario=self.user3,piso=True,fecha_nacimiento="2000-1-1",edad=1,lugar="Sevilla",nacionalidad="Española",
                            genero='F',pronombres="Ella",idiomas="ES",universidad="US",estudios="Informática")
        
        mate = Mates(userEntrada=self.user3, userSalida=self.user1, mate=True)

        self.user1.save()
        self.user2.save()
        self.user3.save()
        perfil1.save()
        perfil2.save()
        perfil3.save()
        mate.save()

    def test_accept_mate(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 1}
        response = self.client.post('/accept-mate/', data, format='json')
        json_resp = json.loads(response.content)
        mate = Mates.objects.get(userEntrada=self.user1, userSalida=self.user2)

        self.assertTrue(mate.mate)
        self.assertTrue(json_resp['success'])
        self.assertFalse(json_resp['mate_achieved'])

    
    def test_reject_mate(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 1}
        response = self.client.post('/reject-mate/', data, format='json')
        json_resp = json.loads(response.content)
        mate = Mates.objects.get(userEntrada=self.user1, userSalida=self.user2)

        self.assertFalse(mate.mate)
        self.assertTrue(json_resp['success'])

    def test_mate_achieved(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 2}
        response = self.client.post('/accept-mate/', data, format='json')
        json_resp = json.loads(response.content)
        mate = Mates.objects.get(userEntrada=self.user1, userSalida=self.user3)

        self.assertTrue(mate.mate)
        self.assertTrue(json_resp['success'])
        self.assertTrue(json_resp['mate_achieved'])

    def test_accept_mate_self(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 0}
        response = self.client.post('/accept-mate/', data, format='json')
        json_resp = json.loads(response.content)

        self.assertFalse(json_resp['success'])

    def test_reject_mate_self(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 0}
        response = self.client.post('/reject-mate/', data, format='json')
        json_resp = json.loads(response.content)

        self.assertFalse(json_resp['success'])

    def test_accept_mate_inexistent_user(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 100}
        response = self.client.post('/accept-mate/', data, format='json')

        self.assertEquals(response.status_code,404)

    def test_reject_mate_inexistent_user(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 100}
        response = self.client.post('/reject-mate/', data, format='json')

        self.assertEquals(response.status_code,404)
    
    def test_accept_mate_not_logged(self):
        data = {'id_us': 0}
        response = self.client.post('/accept-mate/', data, format='json')
        
        self.assertEquals(response.status_code,302)
        self.assertRedirects(response,"/login/", target_status_code=200)

    def test_reject_mate_not_logged(self):
        data = {'id_us': 0}
        response = self.client.post('/reject-mate/', data, format='json')
        
        self.assertEquals(response.status_code,302)
        self.assertRedirects(response,"/login/", target_status_code=200)

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
        perfil = Usuario(usuario=user,piso=True,fecha_nacimiento="2000-1-1",edad=1,lugar="Sevilla",nacionalidad="Española",
                genero='F',pronombres="Ella",idiomas="ES",universidad="US",estudios="Informática")
        user.save()
        perfil.save()
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
