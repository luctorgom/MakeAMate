from django.conf import settings
from django.db import models
from django.forms import NullBooleanField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User


# Create your models here.

#class Foto(models.Model):

class Gustos(models.Model):
    opcionGustos=models.CharField(max_length=40)

    def __str__(self):
        return str(self.opcionGustos)

class Aficiones(models.Model):
    opcionAficiones=models.CharField(max_length=50)

    def __str__(self):
        return str(self.opcionAficiones)

class Tags(models.Model):
    etiqueta=models.CharField(max_length=10)

    def __str__(self):
        return str(self.etiqueta)

class Usuario(models.Model):
    usuario=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    piso=models.BooleanField()
    #foto=models.ForeignKey('Foto')
    fecha_nacimiento=models.DateField()
    edad=models.PositiveSmallIntegerField(validators=[MinValueValidator(18), MaxValueValidator(30)])
    lugar=models.CharField(max_length=10)
    nacionalidad=models.CharField(max_length=10)
    genero= models.CharField(max_length=1,choices=(('F', 'Femenino'),('M','Masculino'),('O','Otro')))
    pronombres=models.CharField(max_length=4,choices=(('Ella', 'Ella'),('El','El'),('Elle','Elle')))
    idiomas=models.CharField(max_length=10,choices=(('ES', 'Español'),('EN','Inglés'),('FR','Francés'),
                                                    ('DE','Alemán'),('PT','Portugués'),('IT','Italiano'),
                                                    ('SV','Sueco'),('OT','Otro')))
    universidad=models.CharField(max_length=40)
    estudios=models.CharField(max_length=40)
    tags=models.ManyToManyField(to=Tags)
    gustos=models.ManyToManyField(to=Gustos)
    aficiones=models.ManyToManyField(to=Aficiones)

    def __str__(self):
        return str(self.usuario)

class Mates(models.Model):
    mate=models.BooleanField(default=NullBooleanField)
    userEntrada=models.ForeignKey(settings.AUTH_USER_MODEL, related_name="entrada", on_delete=models.DO_NOTHING)
    userSalida=models.ForeignKey(settings.AUTH_USER_MODEL, related_name="salida",on_delete=models.DO_NOTHING)

    def __str__(self):
        return str(self.userEntrada.username + "-" + self.userSalida.username + ": " + str(self.mate))
    
    class Meta:
        unique_together = ('userEntrada', 'userSalida',)