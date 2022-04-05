from datetime import date,datetime,timedelta
from django.utils import timezone
import json
from django.test import Client, TestCase
from django.conf import settings
from django.contrib import auth
from .models import Aficiones, Mate, Tag, Usuario, Idioma, Piso, Foto
from django.contrib.auth.models import User

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

        etiquetas= Tag.objects.create(etiqueta="No fumador")
        aficion= Aficiones.objects.create(opcionAficiones="Deportes")
        idioma = Idioma.objects.create(idioma="Español")
        
        piso_maria = Piso.objects.create(zona="Calle Marqués Luca de Tena 3", descripcion="Descripción de prueba 2")
        piso_sara = Piso.objects.create(zona="Calle Marqués Luca de Tena 5", descripcion="Descripción de prueba 3")

        Pepe= Usuario.objects.create(usuario=userPepe, fecha_nacimiento=date(2000,12,31),lugar="Sevilla")
        Maria=Usuario.objects.create(usuario=userMaria, fecha_nacimiento=date(2000,12,30),lugar="Sevilla", piso=piso_maria)
        Sara= Usuario.objects.create(usuario=userSara,fecha_nacimiento=date(2000,12,29),lugar="Cádiz", piso=piso_sara)
    
    

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

        pepe= Usuario.objects.create(usuario=user, piso=piso_pepe, fecha_nacimiento=date(2000,12,31),lugar="Sevilla")
        maria=Usuario.objects.create(usuario=user2, piso=piso_maria, fecha_nacimiento=date(2000,12,30),lugar="Sevilla")
        sara= Usuario.objects.create(usuario=user3, piso=piso_sara,fecha_nacimiento=date(2000,12,29),lugar="Cádiz")

        #MATE ENTRE user y user2
        mate1 = Mate.objects.create(mate=True,userEntrada=user, userSalida=user2)
        mate2 = Mate.objects.create(mate=True,userEntrada=user2, userSalida=user)

        #EL user LE DA MATE AL user3, PERO EL user3 NO LE DA MATE A ÉL
        mate3 = Mate.objects.create(mate=True,userEntrada=user, userSalida=user3)
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

class EstadisticasTest(TestCase):
    
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
        self.user3=user3
        user4 = User(username='usuario4')
        user4.set_password('qwery')
        user4.save()
        self.user4=user4
        
        et1= Tag.objects.create(etiqueta="Netflix")
        et1.save()
        et2=Tag.objects.create(etiqueta="Chill")
        et2.save()
        et3=Tag.objects.create(etiqueta="Fiesta")
        et3.save()
        af1= Aficiones.objects.create(opcionAficiones="Moda")
        af1.save()
        af2= Aficiones.objects.create(opcionAficiones="Cine")
        af2.save()
        af3= Aficiones.objects.create(opcionAficiones="Leer")
        af3.save()

        piso_pepe = Piso.objects.create(zona="Calle Marqués Luca de Tena 1", descripcion="Descripción de prueba 1")
        piso_maria = Piso.objects.create(zona="Calle Marqués Luca de Tena 3", descripcion="Descripción de prueba 2")
        piso_sara = Piso.objects.create(zona="Calle Marqués Luca de Tena 5", descripcion="Descripción de prueba 3")
        piso_juan = Piso.objects.create(zona="Calle Marqués Luca de Tena 4", descripcion="Descripción de prueba ")
        

        fecha_premium=timezone.now() + timedelta(days=120)
        pepe= Usuario.objects.create(usuario=user, piso=piso_pepe, fecha_nacimiento=date(2000,12,31),lugar="Sevilla", fecha_premium=fecha_premium)
        pepe.save()
        pepe.tags.add(et1)
        pepe.tags.add(et2)
        pepe.tags.add(et3)
        pepe.aficiones.add(af1)
        maria=Usuario.objects.create(usuario=user2, piso=piso_maria, fecha_nacimiento=date(2000,12,30),lugar="Sevilla")
        maria.save()
        maria.tags.add(et2)
        maria.aficiones.add(af2)
        sara= Usuario.objects.create(usuario=user3, piso=piso_sara,fecha_nacimiento=date(2000,12,29),lugar="Cádiz")
        sara.save()
        sara.save()
        sara.tags.add(et1)
        sara.tags.add(et3)
        sara.aficiones.add(af2)
        sara.aficiones.add(af3)
        juan= Usuario.objects.create(usuario=user4, piso=piso_juan,fecha_nacimiento=date(2000,1,2),lugar="Granada")
        juan.save()
        juan.save()
        juan.tags.add(et1)
        juan.tags.add(et2)
        juan.aficiones.add(af1)
        juan.aficiones.add(af2)
        juan.aficiones.add(af3)
        #MATE ENTRE user y user2
        mate12 = Mate.objects.create(mate=True,userEntrada=user, userSalida=user2)
        """ mate12.save()
        mate12.fecha_mate.set(datetime(2022,4,4,16,30))
        print(mate12.fecha_mate) """
        mate21 = Mate.objects.create(mate=True,userEntrada=user2, userSalida=user)

        like31 = Mate.objects.create(mate=True,userEntrada=user3, userSalida=user)
        like41 = Mate.objects.create(mate=True,userEntrada=user4, userSalida=user)
        super().setUp()


    #El usuario "user" tiene un mate con user 2 y dos likes de user 2 y user 3 -> Total 3
    def test_interacciones(self):
        c = Client()
        response_user = c.post('/login/', {'username': 'usuario', 'pass': 'qwery'})
        response = c.get('/mates/')
        interacciones = response.context['interacciones']
        self.assertTrue(interacciones == 3)

    #El usuario "user" tiene dos likes de user 2 y user 3 en el mes actual-> Total 2
    def test_likes_mes(self):
        c = Client()
        response_user = c.post('/login/', {'username': 'usuario', 'pass': 'qwery'})
        response = c.get('/mates/')
        likeMes = response.context['lista']
        self.assertTrue(len(likeMes) == 2)

    #El usuario "user" tiene dos likes de user 2 y user 3 en el día de hoy (autoadd)-> Total 2
    def test_likes_hoy(self):
        c = Client()
        response_user = c.post('/login/', {'username': 'usuario', 'pass': 'qwery'})
        response = c.get('/mates/')
        dictLikeFecha = response.context['matesGrafica']
        self.assertTrue(dictLikeFecha[datetime.today().strftime('%d/%m/%Y')] == 3)
    
    #El usuario "user" tiene tags Netflix, Chill y Fiesta
    #El usuario "user3" tiene tags Netflix y Fiesta
    #El usuario "user4" tiene tags Netflix y Chill-> Netflix 2, Chill 1, Fiesta 1
    def test_top_tags(self):
        c = Client()
        response_user = c.post('/login/', {'username': 'usuario', 'pass': 'qwery'})
        response = c.get('/mates/')
        dictTags = response.context['topTags']
        self.assertTrue(dictTags['Netflix'] == 2)
        self.assertTrue(dictTags['Fiesta'] == 1)
        self.assertTrue(dictTags['Chill'] == 1)
    
    #El usuario "user" tiene dos likes de user 2 y user 3 en el día de hoy (autoadd)-> Total 2
    def test_score_likes(self):
        c = Client()
        response_user = c.post('/login/', {'username': 'usuario', 'pass': 'qwery'})
        response = c.get('/mates/')
        scoreLikes = response.context['scoreLikes']
        self.assertTrue(scoreLikes[self.user3] == 62)
        self.assertTrue(scoreLikes[self.user4] == 71)
