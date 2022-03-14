from django.conf import settings
from django.db import models
from django.forms import NullBooleanField
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.

#class Foto(models.Model):

class Gustos(models.Model):
    opcionGustos=models.CharField()

    def __str__(self):
        return str(self.opcionGustos)

class Aficiones(models.Model):
    opcionAficiones=models.CharField()

    def __str__(self):
        return str(self.opcionAficiones)

class Tags(models.Model):
    etiqueta=models.CharField()

    def __str__(self):
        return str(self.etiqueta)

class Usuario(models.Model):
    usuario=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    piso=models.BooleanField()
    #foto=models.ForeignKey('Foto')
    fecha_nacimiento=models.DateField()
    edad=models.PositiveSmallIntegerField(validators=[MinValueValidator(18), MaxValueValidator(30)])
    lugar=models.CharField()
    #nacionalidad=models.CharField()
    genero= models.CharField(max_length=1,choices=(('F', 'Femenino'),('M','Masculino'),('O','Otro')))
    pronombres=models.CharField(max_length=3,choices=(('Ella', 'Ella'),('El','El'),('Elle','Elle')))
    idiomas=models.enums()
    universidad=models.enums()
    estudios=models.CharField()
    tags=models.ManyToManyField()
    gustos=models.ManyToManyField()
    aficiones=models.ManyToManyField()

    def __str__(self):
        return str(self.usuario, self.lugar)

class Mates(models.Model):
    mate=models.BooleanField(default=NullBooleanField)
    userEntrada=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    userSalida=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

    def __str__(self):
        return str(self.mate, self.userEntrada, self.userSalida)