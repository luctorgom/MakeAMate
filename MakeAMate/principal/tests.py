from datetime import date
import json
from tempfile import NamedTemporaryFile
from django.test import Client, TestCase
from django.conf import settings
from django.contrib import auth
from .models import Aficiones, Mate, Tag, Usuario, Idioma, Piso, Foto
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile



# Test mates
# class MateTestCase(TestCase):
#     def setUp(self):

#         self.user1 = User(id=0,username="us1")
#         self.user1.set_password('123')
#         self.user2 = User(id=1,username="us2")
#         self.user2.set_password('123')
#         self.user3 = User(id=2,username="us3")
#         self.user3.set_password('123')


#         tfn1 = "+34666777111"
#         tfn2 = "+34666777222"
#         tfn3 = "+34666777333"
#         perfil1 = Usuario(usuario=self.user1,fecha_nacimiento="2000-1-1",lugar="Sevilla",nacionalidad="Española",
#                             genero='F',estudios="Informática", telefono = tfn1)
#         perfil2 = Usuario(usuario=self.user2,fecha_nacimiento="2000-1-1",lugar="Sevilla",nacionalidad="Española",
#                             genero='F',estudios="Informática", telefono = tfn2)
#         perfil3 = Usuario(usuario=self.user3,fecha_nacimiento="2000-1-1",lugar="Sevilla",nacionalidad="Española",
#                             genero='F',estudios="Informática", telefono = tfn3)

        
#         mate = Mate(userEntrada=self.user3, userSalida=self.user1, mate=True)

#         self.user1.save()
#         self.user2.save()
#         self.user3.save()
#         perfil1.save()
#         perfil2.save()
#         perfil3.save()
#         mate.save()

#     def test_accept_mate(self):
#         self.client.login(username='us1', password='123')

#         data = {'id_us': 1}
#         response = self.client.post('/accept-mate/', data, format='json')
#         json_resp = json.loads(response.content)
#         mate = Mate.objects.get(userEntrada=self.user1, userSalida=self.user2)

#         self.assertTrue(mate.mate)
#         self.assertTrue(json_resp['success'])
#         self.assertFalse(json_resp['mate_achieved'])

    
#     def test_reject_mate(self):
#         self.client.login(username='us1', password='123')

#         data = {'id_us': 1}
#         response = self.client.post('/reject-mate/', data, format='json')
#         json_resp = json.loads(response.content)
#         mate = Mate.objects.get(userEntrada=self.user1, userSalida=self.user2)

#         self.assertFalse(mate.mate)
#         self.assertTrue(json_resp['success'])

#     def test_mate_achieved(self):
#         self.client.login(username='us1', password='123')

#         data = {'id_us': 2}
#         response = self.client.post('/accept-mate/', data, format='json')
#         json_resp = json.loads(response.content)
#         mate = Mate.objects.get(userEntrada=self.user1, userSalida=self.user3)

#         self.assertTrue(mate.mate)
#         self.assertTrue(json_resp['success'])
#         self.assertTrue(json_resp['mate_achieved'])

#     def test_accept_mate_self(self):
#         self.client.login(username='us1', password='123')

#         data = {'id_us': 0}
#         response = self.client.post('/accept-mate/', data, format='json')
#         json_resp = json.loads(response.content)

#         self.assertFalse(json_resp['success'])

#     def test_reject_mate_self(self):
#         self.client.login(username='us1', password='123')

#         data = {'id_us': 0}
#         response = self.client.post('/reject-mate/', data, format='json')
#         json_resp = json.loads(response.content)

#         self.assertFalse(json_resp['success'])

#     def test_accept_mate_inexistent_user(self):
#         self.client.login(username='us1', password='123')

#         data = {'id_us': 100}
#         response = self.client.post('/accept-mate/', data, format='json')

#         self.assertEquals(response.status_code,404)

#     def test_reject_mate_inexistent_user(self):
#         self.client.login(username='us1', password='123')

#         data = {'id_us': 100}
#         response = self.client.post('/reject-mate/', data, format='json')

#         self.assertEquals(response.status_code,404)
    
#     def test_accept_mate_not_logged(self):
#         data = {'id_us': 0}
#         response = self.client.post('/accept-mate/', data, format='json')
        
#         self.assertEquals(response.status_code,302)
#         self.assertRedirects(response,"/login/", target_status_code=200)

#     def test_reject_mate_not_logged(self):
#         data = {'id_us': 0}
#         response = self.client.post('/reject-mate/', data, format='json')
        
#         self.assertEquals(response.status_code,302)
#         self.assertRedirects(response,"/login/", target_status_code=200)

# class FiltesTests(TestCase):
    
#     def setUp(self):
#         super().setUp()
    
#     @classmethod
#     def setUpTestData(cls):
#         userPepe= User(username="Pepe")
#         userPepe.set_password("asdfg")
#         userPepe.save()

#         userMaria=User(username="Maria")
#         userMaria.set_password("asdfg")
#         userMaria.save()

#         userSara=User(username="Sara")
#         userSara.set_password("asdfg")
#         userSara.save()


#         tfn1 = "+34666777111"
#         tfn2 = "+34666777222"
#         tfn3 = "+34666777333"

#         etiquetas= Tag.objects.create(etiqueta="No fumador")
#         aficion= Aficiones.objects.create(opcionAficiones="Deportes")
#         idioma = Idioma.objects.create(idioma="Español")
        
#         piso_maria = Piso.objects.create(zona="Calle Marqués Luca de Tena 3", descripcion="Descripción de prueba 2")
#         piso_sara = Piso.objects.create(zona="Calle Marqués Luca de Tena 5", descripcion="Descripción de prueba 3")


#         Pepe= Usuario.objects.create(usuario=userPepe, fecha_nacimiento=date(2000,12,31),lugar="Sevilla", telefono=tfn1)
#         Maria=Usuario.objects.create(usuario=userMaria, fecha_nacimiento=date(2000,12,30),lugar="Sevilla", piso=piso_maria, telefono=tfn2)
#         Sara= Usuario.objects.create(usuario=userSara,fecha_nacimiento=date(2000,12,29),lugar="Cádiz", piso=piso_sara, telefono=tfn3)

    
    

#    #Nos logeamos como Pepe usuario sin Piso en Sevilla y 
#    # comprobamos que solo nos sale 1 usuario, que es el que esta en la misma ciudad
#     def test_filter_(self):
#         c= Client()
#         login= c.login(username='Pepe', password= 'asdfg')
#         response=c.get('/')

#         self.assertTrue( len(response.context['usuarios']) == 1)
#         self.assertEqual(response.status_code, 200)
       

#     #Nos logeamos como Pepe usuario sin Piso en Sevilla y 
#     #comprobamos que efectivamente no salen 2 usuarios ya que uno de ellos no vive en la misma ciudad
#     def test_filter_error(self):
#         c= Client()
#         c.login(username='Pepe', password= 'asdfg')
#         response=c.get('/')
#         self.assertFalse( len(response.context['usuarios']) == 2)
#         self.assertEqual(response.status_code, 200)

# #Test de login
# class LoginTest(TestCase):
#     def setUp(self):
#         user = User(username='usuario')
#         user.set_password('qwery')
#         tfn = "+34666777444"
#         piso = Piso.objects.create(zona="Calle Marqués Luca de Tena 3", descripcion="Descripción de prueba 2")
#         perfil = Usuario(usuario=user,piso=piso,fecha_nacimiento="2000-1-1",lugar="Sevilla",nacionalidad="Española",
#                 genero='F',estudios="Informática", telefono=tfn)
#         user.save()
#         perfil.save()
#         super().setUp()


#     #Test de inicio de sesión con un usuario existente
#     def test_login_positive(self):
#         c = Client()
#         response = c.post('/login/', {'username': 'usuario', 'pass': 'qwery'})
#         user = auth.get_user(c)
#         self.assertTrue(user.is_authenticated)
#         self.assertRedirects(response, '/', status_code=302, 
#         target_status_code=200, fetch_redirect_response=True)


#     #Test de inicio de sesión con un usuario inexistente
#     def test_login_negative(self):
#         c = Client()
#         response = c.post('/login/', {'username': 'inexistente', 'pass': 'inexistente'})
#         user = auth.get_user(c)
#         self.assertFalse(user.is_authenticated)


# class NotificacionesTest(TestCase):
    
#     def setUp(self):
#         user = User(username='usuario')
#         user.set_password('qwery')
#         user.save()

#         user2 = User(username='usuario2')
#         user2.set_password('qwery')
#         user2.save()

#         user3 = User(username='usuario3')
#         user3.set_password('qwery')
#         user3.save()

#         tfn1 = "+34666777666"
#         tfn2 = "+34666777777"
#         tfn3 = "+34666777888"
#         piso_pepe = Piso.objects.create(zona="Calle Marqués Luca de Tena 1", descripcion="Descripción de prueba 1")   
#         piso_maria = Piso.objects.create(zona="Calle Marqués Luca de Tena 3", descripcion="Descripción de prueba 2")
#         piso_sara = Piso.objects.create(zona="Calle Marqués Luca de Tena 5", descripcion="Descripción de prueba 3")

#         pepe= Usuario.objects.create(usuario=user, piso=piso_pepe, fecha_nacimiento=date(2000,12,31),lugar="Sevilla", telefono=tfn1)
#         maria=Usuario.objects.create(usuario=user2, piso=piso_maria, fecha_nacimiento=date(2000,12,30),lugar="Sevilla", telefono=tfn2)
#         sara= Usuario.objects.create(usuario=user3, piso=piso_sara,fecha_nacimiento=date(2000,12,29),lugar="Cádiz",telefono=tfn3)

#         #MATE ENTRE user y user2
#         mate1 = Mate.objects.create(mate=True,userEntrada=user, userSalida=user2)
#         mate2 = Mate.objects.create(mate=True,userEntrada=user2, userSalida=user)

#         #EL user LE DA MATE AL user3, PERO EL user3 NO LE DA MATE A ÉL
#         mate3 = Mate.objects.create(mate=True,userEntrada=user, userSalida=user3)
#         super().setUp()


#     #El usuario "user" tiene un mate, por lo que su lista de mates será de tamaño 1
#     def test_notificaciones(self):
#         c = Client()
#         response_user = c.post('/login/', {'username': 'usuario', 'pass': 'qwery'})
#         response2 = c.get('/')
#         lista_mates = response2.context['notificaciones']

#         self.assertTrue(len(lista_mates) == 1)

#     #El usuario "user3" no tiene ningún mate, por lo que su lista de mates será de tamaño 0
#     def test_notificaciones_2(self):
#         c = Client()
#         response = c.post('/login/', {'username': 'usuario3', 'pass': 'qwery'})
#         response2 = c.get('/')
#         lista_mates = response2.context['notificaciones']
#         self.assertTrue(len(lista_mates) == 0)


class RegistroTest(TestCase):

    def setUp(self):

        Tag.objects.create(etiqueta='etiqueta1').save()
        Tag.objects.create(etiqueta='etiqueta2').save()
        Tag.objects.create(etiqueta='etiqueta3').save()


        Aficiones.objects.create(opcionAficiones='Aficion1').save()
        Aficiones.objects.create(opcionAficiones='Aficion2').save()
        Aficiones.objects.create(opcionAficiones='Aficion3').save()


        self.data = {
            'username':'usuariotest',
            'password':'passwordtest1',
            'password2': 'passwordtest1',
            'nombre': 'nombreprueba',
            'apellidos':'apellidosprueba',
            'correo':'prueba@gmail.com',
            'zona_piso':'Ejemplo de zona',
            'telefono_usuario':'+34666777888',
            'foto_usuario': SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg'),
            'fecha_nacimiento':'01-01-2000',
            'lugar':'Ejemplo de lugar',
            'nacionalidad':'Ejemplo',
            'genero':'M',
            'tags': Tag.objects.all(),
            'aficiones': Aficiones.objects.all()

        }
        super().setUp()

    def test_registro_positive(self):
        c = Client()
        response = c.post('/register/', self.data)
        existe_usuario = Usuario.objects.filter(telefono=self.data['telefono_usuario']).exists()
        self.assertTrue(response.status_code == 200)
        self.assertTrue(existe_usuario)

