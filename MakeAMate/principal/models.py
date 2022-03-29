from django.conf import settings
from django.db import models
from django.forms import NullBooleanField
from django.core.validators import MaxValueValidator, MinValueValidator,RegexValidator
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


# Create your models here.
class Aficiones(models.Model):
    opcionAficiones=models.CharField(max_length=50)

    def __str__(self):
        return str(self.opcionAficiones)

class Tag(models.Model):
    etiqueta=models.CharField(max_length=40)

    def __str__(self):
        return str(self.etiqueta)

class Idioma(models.Model):
    idioma=models.CharField(max_length=20)

    def __str__(self):
        return str(self.idioma)        

class Piso(models.Model):
    zona=models.CharField(max_length=100)
    descripcion=models.CharField(max_length=1000, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.zona)

class Usuario(models.Model):
    usuario=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    piso=models.OneToOneField(to=Piso, on_delete=models.CASCADE, default=None, blank=True, null=True)
    fecha_nacimiento=models.DateField()
    lugar=models.CharField(max_length=40)
    nacionalidad=models.CharField(max_length=20)
    genero= models.CharField(max_length=1,choices=(('F', 'Femenino'),('M','Masculino'),('O','Otro')))  
    estudios=models.CharField(max_length=40)
    idiomas=models.ManyToManyField(Idioma)
    tags=models.ManyToManyField(Tag)
    aficiones=models.ManyToManyField(Aficiones)
    telefono_regex = RegexValidator(regex = r"^\+[1-9]\d{1,14}$")
    telefono = models.CharField(validators = [telefono_regex], max_length = 16, unique = True)
    passcode=models.CharField(max_length=128, default=None, blank=True, null=True)
    piso_encontrado=models.BooleanField(default=False)
    fecha_premium=models.DateTimeField(blank=True, default=None, null=True)
    descripcion=models.CharField(max_length=1000, default=None, blank=True, null=True)
    foto=models.ImageField(upload_to="principal/static/images/users")

    @classmethod
    def get_edad(cls):
        today = date.today()
        return today.year - cls.fecha_nacimiento.year - ((today.month, today.day) < (cls.fecha_nacimiento.month, cls.fecha_nacimiento.day))

    @classmethod
    def tiene_piso(cls):
        return True if cls.piso != None else False

    @classmethod
    def es_premium(cls):
        if cls.fecha_premium==None:
            return False
        today = datetime.time
        fecha_premium_fin = cls.fecha_premium + relativedelta(months=+1)

        return True if fecha_premium_fin > today else False

    def __str__(self):
        return str(self.usuario)

class Foto(models.Model):
    titulo=models.CharField(max_length=30)
    foto=models.ImageField(upload_to="principal/static/images/pisos")
    piso=models.ForeignKey(Piso, on_delete=models.CASCADE, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.titulo)        

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