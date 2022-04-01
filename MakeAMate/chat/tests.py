from tabnanny import verbose
from django.test import TestCase, Client
from django.contrib import auth
from .models import ChatRoom
from principal.models import Usuario, Mates
from django.contrib.auth.models import User

# Create your tests here.

class ChatTest(TestCase):
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

        perfil1 = Usuario(usuario= user1,piso=True,fecha_nacimiento="2000-1-1",edad=1,lugar="Sevilla",nacionalidad="Española",
                            genero='F',pronombres="Ella",idiomas="ES",universidad="US",estudios="Informática")
        perfil2 = Usuario(usuario= user2,piso=True,fecha_nacimiento="2000-1-1",edad=1,lugar="Sevilla",nacionalidad="Española",
                            genero='F',pronombres="Ella",idiomas="ES",universidad="US",estudios="Informática")
        perfil3 = Usuario(usuario= user3,piso=True,fecha_nacimiento="2000-1-1",edad=1,lugar="Sevilla",nacionalidad="Española",
                            genero='F',pronombres="Ella",idiomas="ES",universidad="US",estudios="Informática")
        perfil4 = Usuario(usuario= user4,piso=True,fecha_nacimiento="2000-1-1",edad=1,lugar="Sevilla",nacionalidad="Española",
                            genero='F',pronombres="Ella",idiomas="ES",universidad="US",estudios="Informática")
        perfil5 = Usuario(usuario= user5,piso=True,fecha_nacimiento="2000-1-1",edad=1,lugar="Sevilla",nacionalidad="Española",
                            genero='F',pronombres="Ella",idiomas="ES",universidad="US",estudios="Informática")


        mate12 = Mates(userEntrada= user1, userSalida= user2, mate=True)
        mate21 = Mates(userEntrada= user2, userSalida= user1, mate=True)
        mate13 = Mates(userEntrada= user1, userSalida= user3, mate=True)
        mate31 = Mates(userEntrada= user3, userSalida= user1, mate=True)
        # mate41 = Mates(userEntrada= user4, userSalida= user1, mate=True)

        set_participants = { user1,  user2}

        chat1 = ChatRoom(name=1)


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

        #Hay 5 usuarios en la base de datos
        self.assertEqual(len(response.context['nombrechats']),5)
    def test_chat_user5_index(self):
        c = Client()
        login = c.login(username='us5', password= '123')
        response=c.get('/chat/')

        #El usuario 5 no tiene chats, con lo cual se le redirige a /
        self.assertRedirects(response, "/")

    def test_chat_user1_chatroom(self):
        c = Client()
        login = c.login(username='us1', password= '123')
        response=c.get('/chat/1/')

        self.assertEqual(response.context['room_name'],"1")

        #El usuario 1 ha hecho mate con 2 usuarios
        self.assertEqual(len(response.context['users']),2)

        #El usuario 1 tiene un chat
        self.assertEqual(len(response.context['chats']),1)

        #Hay 5 usuarios en la base de datos
        self.assertEqual(len(response.context['nombrechats']),5)





