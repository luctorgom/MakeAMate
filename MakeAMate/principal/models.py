from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.forms import NullBooleanField
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from datetime import date, datetime
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator,RegexValidator
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone

BASE_CLOUDIFY_URL = "https://res.cloudinary.com/deqjxxfzm/image/upload/v1/"

# Create your models here.
class Aficiones(models.Model):
    opcionAficiones=models.CharField(max_length=50)

    def __str__(self):
        return str(self.opcionAficiones)

class Tag(models.Model):
    etiqueta=models.CharField(max_length=40)

    def __str__(self):
        return str(self.etiqueta)     

class Piso(models.Model):
    zona=models.CharField(max_length=100, default=None, blank=True, null=True)
    descripcion=models.CharField(max_length=1000, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.zona)
        
class Foto(models.Model):
    titulo=models.CharField(max_length=30)
    foto=models.ImageField(upload_to="images/pisos")
    piso=models.ForeignKey(Piso, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.titulo)

    def url_piso_relativa(self):
        return BASE_CLOUDIFY_URL+str(self.foto) 

class Usuario(models.Model):
    usuario=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    piso=models.ForeignKey(to=Piso, on_delete=models.SET_NULL, default=None, blank=True, null=True)
    fecha_nacimiento=models.DateField()
    lugar=models.CharField(max_length=40)
    #nacionalidad=models.CharField(max_length=20)
    genero= models.CharField(max_length=1,choices=(('F', 'Femenino'),('M','Masculino'),('O','Otro')))  
    estudios=models.CharField(max_length=40, default=None, null=True, blank=True)
    tags=models.ManyToManyField(Tag)
    aficiones=models.ManyToManyField(Aficiones)
    piso_encontrado=models.BooleanField(default=False)
    fecha_premium=models.DateTimeField(blank=True, default=None, null=True)
    descripcion=models.CharField(max_length=1000, default=None, null=True, blank=True)
    foto=models.ImageField(upload_to="images/users")
    telefono_regex = RegexValidator(regex = r"^\+[1-9]\d{1,14}$")
    telefono = models.CharField(validators = [telefono_regex], max_length = 16, unique = True)
    sms_validado=models.BooleanField(default=False)

    def get_edad(self):
        today = date.today()
        return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))

    def tiene_piso(self):
        return self.piso != None

    def es_premium(self):
        if self.fecha_premium==None:
            return False
        today = timezone.now()
        
        return self.fecha_premium > today

    def url_perfil_relativa(self):
        return BASE_CLOUDIFY_URL+str(self.foto)


    def __str__(self):
        return str(self.usuario)         
    

class Mate(models.Model):
    mate=models.BooleanField(default=NullBooleanField)
    userEntrada=models.ForeignKey(settings.AUTH_USER_MODEL, related_name="entrada", on_delete=models.CASCADE)
    userSalida=models.ForeignKey(settings.AUTH_USER_MODEL, related_name="salida",on_delete=models.CASCADE)
    fecha_mate=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.userEntrada.username + "-" + self.userSalida.username + ": " + str(self.mate))
    
    class Meta:
        unique_together = ('userEntrada', 'userSalida',)

class Oferta(models.Model):
    precio=models.DecimalField(max_digits=6, decimal_places=2)
    descuento=models.FloatField(default=0)
    duracion_meses=models.IntegerField()

    def __str__(self):
        return str("Precio = " + str(self.precio) + ", descuento = " + str(self.descuento) + ", duración = " + str(self.duracion_meses))