from django.test import TestCase, Client
from chat.models import ChatRoom
from principal.models import Usuario, Mate
from django.contrib.auth.models import User
from channels.testing import WebsocketCommunicator
from chat.consumers import WebsocketConsumer
from channels.testing import WebsocketCommunicator
from django.core.exceptions import PermissionDenied
# Create your tests here.

class ChatTestCase(TestCase):
    def setUp(self):
        user1 = User(id=0,username="us1")
        user1.set_password('123')
        user2 = User(id=1,username="us2")
        user2.set_password('123')
        user3 = User(id=2,username="us3")
        user3.set_password('123')
        user4 = User(id=3,username="us4")
        user4.set_password('123')
        user5 = User(id=4,username="us5")
        user5.set_password('123')

        perfil1 = Usuario(usuario= user1,fecha_nacimiento="2000-1-1",lugar="Sevilla", telefono="+34666666661",
                            genero='F',estudios="Informática",sms_validado=True)
        perfil2 = Usuario(usuario= user2,fecha_nacimiento="2000-1-1",lugar="Sevilla", telefono="+34666666662",
                            genero='F',estudios="Informática",sms_validado=True)
        perfil3 = Usuario(usuario= user3,fecha_nacimiento="2000-1-1",lugar="Sevilla", telefono="+34666666663",
                            genero='F',estudios="Informática",sms_validado=True)
        perfil4 = Usuario(usuario= user4,fecha_nacimiento="2000-1-1",lugar="Sevilla", telefono="+34666666664",
                            genero='F',estudios="Informática",sms_validado=True)
        perfil5 = Usuario(usuario= user5,fecha_nacimiento="2000-1-1",lugar="Sevilla", telefono="+34666666665",
                            genero='F',estudios="Informática",sms_validado=True)


        mate12 = Mate(userEntrada= user1, userSalida= user2, mate=True)
        mate21 = Mate(userEntrada= user2, userSalida= user1, mate=True)
        mate13 = Mate(userEntrada= user1, userSalida= user3, mate=True)
        mate31 = Mate(userEntrada= user3, userSalida= user1, mate=True)
        # mate41 = Mates(userEntrada= user4, userSalida= user1, mate=True)

        set_participants = { user1,  user2}

        chat1 = ChatRoom(name=5)


        mate12.save()
        mate21.save()
        mate13.save()
        mate31.save()
        # mate41.save()

        user1.save()
        user2.save()
        user3.save()
        user4.save()
        user5.save()
        perfil1.save()
        perfil2.save()
        perfil3.save()
        perfil4.save()
        perfil5.save()

        chat1.save()
        chat1.participants.set([ user1,  user2])
        chat1.save()



    def test_chat_user1_index(self):
        c = Client()
        login = c.login(username='us1', password= '123')
        response=c.get('/chat/')

        #El usuario 1 ha hecho mate con 2 usuarios
        self.assertEqual(len(response.context['users']),2)

        #El usuario 1 tiene un chat
        self.assertEqual(len(response.context['chats']),1)

        #Hay 4 usuarios en la base de datos distintos del logeado
        self.assertEqual(len(response.context['nombrechats']),4)

    def test_chat_user5_index(self):
        c = Client()
        login = c.login(username='us5', password= '123')
        response=c.get('/chat/')

        #El usuario 5 no tiene chats, con lo cual salta error de permiso
        self.assertRaises(PermissionDenied)

    def test_chat_user1_chatroom(self):
        c = Client()
        login = c.login(username='us1', password= '123')
        response=c.get('/chat/5/')

        self.assertEqual(response.context['room_name'],"5")

        #El usuario 1 ha hecho mate con 2 usuarios
        self.assertEqual(len(response.context['users']),2)

        #El usuario 1 tiene un chat
        self.assertEqual(len(response.context['chats']),1)

        #Hay 5 usuarios en la base de datos
        self.assertEqual(len(response.context['nombrechats']),4)

    def test_chat_user5_chatroom(self):
        c = Client()
        login = c.login(username='us5', password= '123')
        response=c.get('/chat/5/')

        #El usuario 5 no tiene chats, con lo cual salta error de permiso
        self.assertRaises(PermissionDenied)

        response=c.get('/chat/20/')
        
        #El usuario 5 ha intentado forzar la url yendo a un chat que no existe, con lo cual salta error de permiso
        self.assertRaises(PermissionDenied)

    def test_anon_user(self):
        c = Client()
        response=c.get('/chat/')

        #El usuario anónimo no puede acceder, con lo cual salta error de permiso
        self.assertRaises(PermissionDenied)

        #El usuario anónimo no puede acceder, con lo cual salta error de permiso
        response2=c.get('/chat/5/')
        self.assertRaises(PermissionDenied)

    '''def test_form_group_positive(self):
        c = Client()
        login = c.login(username='us1', password= '123')

        #Se rellena el formulario
        response=c.post('/chat/', data = {'Nombre':'GrupoTest','Personas': [1,2]})

        #Se comprueba que haya un chat más
        response2 = c.get('/chat/')
        self.assertEqual(len(response2.context['chats']),2)

        #Se comprueba que el nombre del chat sea GrupoTest
        response3 = c.get('/chat/1/')
        self.assertEqual(response3.context['nombre_sala'], 'GrupoTest')'''

    async def test_consumer(self):
        application = WebsocketConsumer.as_asgi()
        communicator = WebsocketCommunicator(application, path="/chat/5/")
        connected, subprotocol = await communicator.connect()
        assert connected
        await communicator.send_to(text_data="hola")
        await communicator.disconnect()
