from datetime import date, timedelta, datetime
import json
from django.test import Client, TestCase
from django.conf import settings
from django.contrib import auth
from .models import Aficiones, Mate, Tag, Usuario, Idioma, Piso, Foto
from django.contrib.auth.models import User
from django.utils import timezone

# Test mates
class MateTestCase(TestCase):
    def setUp(self):

        self.user1 = User(id=0,username="us1")
        self.user1.set_password('123')
        self.user2 = User(id=1,username="us2")
        self.user2.set_password('123')
        self.user3 = User(id=2,username="us3")
        self.user3.set_password('123')

        perfil1 = Usuario(usuario=self.user1,fecha_nacimiento="2000-1-1",lugar="Sevilla",nacionalidad="Española",
                            genero='F',estudios="Informática")
        perfil2 = Usuario(usuario=self.user2,fecha_nacimiento="2000-1-1",lugar="Sevilla",nacionalidad="Española",
                            genero='F',estudios="Informática")
        perfil3 = Usuario(usuario=self.user3,fecha_nacimiento="2000-1-1",lugar="Sevilla",nacionalidad="Española",
                            genero='F',estudios="Informática")
        
        mate = Mate(userEntrada=self.user3, userSalida=self.user1, mate=True)

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
        mate = Mate.objects.get(userEntrada=self.user1, userSalida=self.user2)

        self.assertTrue(mate.mate)
        self.assertTrue(json_resp['success'])
        self.assertFalse(json_resp['mate_achieved'])

    
    def test_reject_mate(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 1}
        response = self.client.post('/reject-mate/', data, format='json')
        json_resp = json.loads(response.content)
        mate = Mate.objects.get(userEntrada=self.user1, userSalida=self.user2)

        self.assertFalse(mate.mate)
        self.assertTrue(json_resp['success'])

    def test_mate_achieved(self):
        self.client.login(username='us1', password='123')

        data = {'id_us': 2}
        response = self.client.post('/accept-mate/', data, format='json')
        json_resp = json.loads(response.content)
        mate = Mate.objects.get(userEntrada=self.user1, userSalida=self.user3)

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
        self.userPepe= User(username="Pepe")
        self.userPepe.set_password("asdfg")
        self.userPepe.save()

        userMaria=User(username="Maria")
        userMaria.set_password("asdfg")
        userMaria.save()

        userSara=User(username="Sara")
        userSara.set_password("asdfg")
        userSara.save()

        self.userPepa=User(username="Pepa")
        self.userPepa.set_password("asdfg")
        self.userPepa.save()

        self.userJuan=User(username="Juan")
        self.userJuan.set_password("asdfg")
        self.userJuan.save()

        etiquetas= Tag.objects.create(etiqueta="No fumador")
        aficion= Aficiones.objects.create(opcionAficiones="Deportes")
        idioma = Idioma.objects.create(idioma="Español")
        
        piso_maria = Piso.objects.create(zona="Calle Marqués Luca de Tena 3", descripcion="Descripción de prueba 2")
        piso_sara = Piso.objects.create(zona="Calle Marqués Luca de Tena 5", descripcion="Descripción de prueba 3")

        Pepe= Usuario.objects.create(usuario=self.userPepe, fecha_nacimiento=date(2000,12,31),lugar="Sevilla")
        Maria=Usuario.objects.create(usuario=userMaria, fecha_nacimiento=date(2000,12,30),lugar="Sevilla", piso=piso_maria)
        Sara= Usuario.objects.create(usuario=userSara,fecha_nacimiento=date(2000,12,29),lugar="Cádiz", piso=piso_sara)
        Pepa=Usuario.objects.create(usuario=self.userPepa, fecha_nacimiento=date(2000,12,28), lugar="Sevilla")
        Juan=Usuario.objects.create(usuario=self.userJuan, fecha_nacimiento=date(2000,12,27), lugar ="Sevilla")
    
    

   #Nos logeamos como Pepe usuario sin Piso en Sevilla y 
   # comprobamos que solo nos sale 1 usuario, que es el que esta en la misma ciudad
    def test_filter_piso_y_ciudad(self):
        c= Client()
        login= c.login(username='Pepe', password= 'asdfg')
        response=c.get('/')

        self.assertTrue( len(response.context['usuarios']) == 3)
        self.assertEqual(response.status_code, 200)
       

    #Nos logeamos como Pepe usuario sin Piso en Sevilla y 
    #comprobamos que efectivamente no salen 2 usuarios ya que uno de ellos no vive en la misma ciudad
    def test_filter_error(self):
        c= Client()
        c.login(username='Pepe', password= 'asdfg')
        response=c.get('/')
        self.assertFalse( len(response.context['usuarios']) == 4)
        self.assertEqual(response.status_code, 200)

    def test_filter_rejected_mate(self):
        c= Client()
        c.login(username='Pepe', password= 'asdfg')
        response=c.get('/')
        #Comprombamos que antes de rechazar a un usuario nos salen 3 en total
        self.assertTrue( len(response.context['usuarios']) == 3)
        mate=Mate.objects.create(userEntrada=self.userPepe, userSalida=self.userPepa, mate=False)
        response=c.get('/')
        #Comprobamos que tras rechazar a un usuario ese ya no nos aparece como usuario recomendado
        self.assertTrue( len(response.context['usuarios']) == 2)

    def test_filter_accepted_mate(self):
        c= Client()
        c.login(username='Pepe', password= 'asdfg')
        response=c.get('/')
        #Comprombamos que antes de hacer mate con un usuario nos salen 3 en total
        self.assertTrue( len(response.context['usuarios']) == 3)
        mate=Mate.objects.create(userEntrada=self.userPepe, userSalida=self.userJuan, mate=True)
        response=c.get('/')
        #Comprobamos que tras hacer mate con un usuario ese ya no nos aparece como usuario recomendado
        self.assertTrue( len(response.context['usuarios']) == 2)
    


#Test de login
class LoginTest(TestCase):
    def setUp(self):
        user = User(username='usuario')
        user.set_password('qwery')
        piso = Piso.objects.create(zona="Calle Marqués Luca de Tena 3", descripcion="Descripción de prueba 2")
        perfil = Usuario(usuario=user,piso=piso,fecha_nacimiento="2000-1-1",lugar="Sevilla",nacionalidad="Española",
                genero='F',estudios="Informática")
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

        piso_pepe = Piso.objects.create(zona="Calle Marqués Luca de Tena 1", descripcion="Descripción de prueba 1")   
        piso_maria = Piso.objects.create(zona="Calle Marqués Luca de Tena 3", descripcion="Descripción de prueba 2")
        piso_sara = Piso.objects.create(zona="Calle Marqués Luca de Tena 5", descripcion="Descripción de prueba 3")
        
        fecha_premium=timezone.now() + timedelta(days=120)
        pepe= Usuario.objects.create(usuario=user, piso=piso_pepe, fecha_nacimiento=date(2000,12,31),lugar="Sevilla", fecha_premium=fecha_premium)
        maria=Usuario.objects.create(usuario=user2, piso=piso_maria, fecha_nacimiento=date(2000,12,30),lugar="Sevilla")
        sara= Usuario.objects.create(usuario=user3, piso=piso_sara,fecha_nacimiento=date(2000,12,29),lugar="Cádiz")

        #MATE ENTRE user y user2
        mate12 = Mate.objects.create(mate=True,userEntrada=user, userSalida=user2)
        mate21 = Mate.objects.create(mate=True,userEntrada=user2, userSalida=user)

        #EL user3 LE DA LIKE al user1 y al user 2
        like31 = Mate.objects.create(mate=True,userEntrada=user3, userSalida=user)
        like32= Mate.objects.create(mate=True,userEntrada=user3, userSalida=user2)
        super().setUp()


    #El usuario "user" tiene un mate y como es premium tb tiene un like, la lista será de tamaño 2
    def test_notificaciones_premium(self):
        c = Client()
        response_user = c.post('/login/', {'username': 'usuario', 'pass': 'qwery'})
        response2 = c.get('/')
        lista_mates = response2.context['notificaciones']

        self.assertTrue(len(lista_mates) == 2)
        
    #El usuario "user2" tiene un mate y un like, la lista será de tamaño 1 porque al no ser premium el like
    #no se le notifica
    def test_notificaciones_no_premium(self):
        c = Client()
        response = c.post('/login/', {'username': 'usuario2', 'pass': 'qwery'})
        response2 = c.get('/')
        lista_mates = response2.context['notificaciones']
        self.assertTrue(len(lista_mates) == 1)
    
    #El usuario "user3" no tiene ningún mate ni like, por lo que su lista de mates será de tamaño 0
    def test_notificaciones_false(self):
        c = Client()
        response = c.post('/login/', {'username': 'usuario3', 'pass': 'qwery'})
        response2 = c.get('/')
        lista_mates = response2.context['notificaciones']
        self.assertTrue(len(lista_mates) == 0)
