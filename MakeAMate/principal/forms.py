from django import forms
from django.conf import settings
from principal.models import Idioma, Aficiones, Tag, Usuario
from django.contrib.auth.models import User
import re
from datetime import *


class SmsForm(forms.Form):
    codigo = forms.CharField(required=True)

class UsuarioForm(forms.Form):
    username = forms.CharField(max_length=100, min_length= 5,
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Usuario'}))
    password = forms.CharField(required=True,widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))
    password2 = forms.CharField(required=True,widget=forms.PasswordInput(attrs={'placeholder': 'Confirma la contraseña'}))
    nombre = forms.CharField(required=True,min_length = 1, max_length = 150, widget=forms.TextInput(attrs={'placeholder': 'Nombre'}))
    apellidos = forms.CharField(required=True, min_length= 1, max_length = 150,widget=forms.TextInput(attrs={'placeholder': 'Apellidos'}))
    correo = forms.EmailField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Correo Electrónico'}))

    zona_piso = forms.CharField(required = False, max_length = 100, widget=forms.TextInput(attrs={'placeholder': 'La Macarena'}))
    telefono_usuario = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '+34675942602'}))

    foto_usuario = forms.ImageField(label="Fotos")
    fecha_nacimiento = forms.DateField(required=True,widget=forms.DateInput(attrs={'placeholder': 'dd-mm-yyyy'}), input_formats=settings.DATE_INPUT_FORMATS)
    lugar = forms.CharField(required=True,max_length=40,widget=forms.TextInput(attrs={'placeholder': 'Ciudad de estudios'}))
    nacionalidad = forms.CharField(required=True,max_length=20,widget=forms.TextInput(attrs={'placeholder': 'Nacionalidad'}))
    genero = forms.ChoiceField(choices=(('F', 'Femenino'),('M','Masculino'),('O','Otro')),required=True)
    idiomas = forms.ModelMultipleChoiceField(queryset=Idioma.objects.all(), widget=forms.CheckboxSelectMultiple)
    tags = forms.ModelMultipleChoiceField(label='¿Qué etiquetas te definen?',queryset=Tag.objects.all(), widget=forms.CheckboxSelectMultiple)
    aficiones = forms.ModelMultipleChoiceField(label='¿Qué aficiones tienes?',queryset=Aficiones.objects.all(), widget=forms.CheckboxSelectMultiple)

    #fotos_piso = forms.FileField(label="Fotos de tu piso")

    ##pronombres = forms.ChoiceField(choices=(('Ella', 'Ella'),('El','El'),('Elle','Elle')),required=True)   
    ##universidad = forms.CharField(required=True,max_length=40,widget=forms.TextInput(attrs={'placeholder': 'Centro de estudios'}))
    ##estudios = forms.CharField(required=True,max_length=40,widget=forms.TextInput(attrs={'placeholder': 'Estudios'}))
    ##descripcion = forms.CharField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Descripción'}))

    # Validación del formulario
    def clean_username(self):
        #Se obtienen los datos del formulario
        #super(UsuarioForm, self).clean()

        username = self.cleaned_data.get('username')

        if len(username) < 5:
            raise forms.ValidationError('El nombre de usuario debe tener una longitud mínima de 5 caracteres')

        if len(username) > 100:
            raise forms.ValidationError('El nombre de usuario debe tener una longitud máxima de 100 caracteres')

        user_exists = User.objects.filter(username=username).exists()

        if(user_exists):
            raise forms.ValidationError('El nombre de usuario ya existe.')

        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        regex = re.compile("^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$")
        if not re.fullmatch(regex, password):
            raise forms.ValidationError('La contraseña debe contener como mínimo 8 caracteres, entre ellos una letra y un número')
        return password

    def clean_password2(self):

        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if not password2:
            raise forms.ValidationError('Por favor, confirma tu contraseña')
        if password != password2:
            raise forms.ValidationError('Las contraseñas no coinciden')

        return password2

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if len(nombre) < 1:
            raise forms.ValidationError('El nombre tiene que contener como mínimo un carácter')        

        if len(nombre) > 150:
            raise forms.ValidationError('El nombre debe tener menos de 150 caracteres')
        return nombre

    def clean_apellidos(self):
        apellidos = self.cleaned_data.get('apellidos')
        if len(apellidos) < 1:
            raise forms.ValidationError('Los apellidos tienen que contener como mínimo un carácter')        

        if len(apellidos) > 150:
            raise forms.ValidationError('Los apellidos deben tener menos de 150 caracteres')

        return apellidos

    def clean_correo(self):
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        correo = self.cleaned_data.get('correo')
        if not re.fullmatch(regex, correo):
            raise forms.ValidationError('Inserte un correo electrónico válido')

        existe_email = User.objects.filter(email=correo).exists()

        if existe_email:
            raise forms.ValidationError('La dirección de correo electrónico ya está en uso')

        return correo

    # def clean_piso(self):
    #     piso = self.cleaned_data.get('piso')
    #     print(piso)
    #     if piso:
    #         raise forms.ValidationError('Indica si tienes piso')

    #     return piso

   # def clean_foto_usuario(self):

    def clean_fecha_nacimiento(self):
        hoy = datetime.now().date()
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento > hoy:
            raise forms.ValidationError('La fecha de nacimiento no puede ser posterior a la fecha actual')

        today = date.today()
        edad = today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        if edad < 18:
            raise forms.ValidationError('Tienes que ser mayor de edad')

        return fecha_nacimiento

    def clean_lugar(self):
        lugar = self.cleaned_data.get('lugar')
        if len(lugar) > 40:
            raise forms.ValidationError('El lugar debe contener menos de 40 caracteres')

        return lugar

    def clean_nacionalidad(self):
        nacionalidad = self.cleaned_data.get('nacionalidad')
        if len(nacionalidad) > 20:
            raise forms.ValidationError('La nacionalidad debe contener menos de 20 caracteres')

        return nacionalidad

    def clean_genero(self):
        genero = self.cleaned_data.get('genero')
        generos = ['M', 'F', 'O']
        if genero not in generos:
            raise forms.ValidationError('El género debe ser Masculino, Femenino u Otro')

        return genero

    def clean_idiomas(self):
        idiomas = self.cleaned_data.get('idiomas')
        if idiomas.count() == 0:
            raise forms.ValidationError('Por favor, elige al menos un idioma')

        return idiomas

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if tags.count() < 3:
            raise forms.ValidationError('Por favor, elige al menos tres etiquetas que te definan')

        return tags

    def clean_aficiones(self):
        aficiones = self.cleaned_data.get('aficiones')
        if aficiones.count() < 3:
            raise forms.ValidationError('Por favor, elige al menos tres aficiones que te gusten')

        return aficiones

    def clean_telefono_usuario(self):
        telefono_usuario = self.cleaned_data.get('telefono_usuario')
        regex = re.compile(r"^\+\d{1,3}\d{9}$")

        if not re.fullmatch(regex, telefono_usuario):
            raise forms.ValidationError('Inserte un teléfono válido')

        existe_telefono = Usuario.objects.filter(telefono=telefono_usuario).exists()

        if existe_telefono:
            raise forms.ValidationError('El teléfono ya está en uso')

        return telefono_usuario

    def clean_zona_piso(self):
        piso = self.cleaned_data.get('zona_piso')
        caracteres = len(piso)

        if caracteres > 100:
            raise forms.ValidationError("La zona debe tener menos de 100 caracteres")       
        return piso

#Formulario para editar perfil
class UsuarioFormEdit(forms.Form):
    zona_piso = forms.CharField(required = False, max_length = 100, error_messages={'required': 'El campo es obligatorio'}, widget=forms.TextInput(attrs={'placeholder': 'La Macarena'}))
    foto_usuario = forms.ImageField(label="Foto", error_messages={'required': 'El campo es obligatorio'})
    lugar = forms.CharField(required=True,error_messages={'required': 'El campo es obligatorio'},max_length=40,widget=forms.TextInput(attrs={'placeholder': 'Ciudad de estudios'}))
    genero = forms.ChoiceField(choices=(('F', 'Femenino'),('M','Masculino'),('O','Otro')),error_messages={'required': 'El campo es obligatorio'},required=True)
    piso_encontrado = forms.ChoiceField(error_messages={'required': 'El campo es obligatorio'},choices=(('False', 'False'),('True','True')))
    descripcion = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Escriba aquí su descripción'}))

    idiomas = forms.ModelMultipleChoiceField(error_messages={'required': 'El campo es obligatorio'},queryset=Idioma.objects.all(), widget=forms.CheckboxSelectMultiple)
    tags = forms.ModelMultipleChoiceField(error_messages={'required': 'El campo es obligatorio'},label='¿Qué etiquetas te definen?',queryset=Tag.objects.all(), widget=forms.CheckboxSelectMultiple)
    aficiones = forms.ModelMultipleChoiceField(error_messages={'required': 'El campo es obligatorio'},label='¿Qué aficiones tienes?',queryset=Aficiones.objects.all(), widget=forms.CheckboxSelectMultiple)

    def clean_zona_piso(self):
        piso = self.cleaned_data.get('zona_piso')
        caracteres = len(piso)

        if caracteres > 100:
            raise forms.ValidationError("La zona debe tener menos de 100 caracteres")
        
        return piso

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if tags.count() < 3:
            raise forms.ValidationError('Por favor, elige al menos tres etiquetas que te definan')

        return tags

    def clean_aficiones(self):
        aficiones = self.cleaned_data.get('aficiones')
        if aficiones.count() < 3:
            raise forms.ValidationError('Por favor, elige al menos tres aficiones que te gusten')

        return aficiones

    def clean_idiomas(self):
        idiomas = self.cleaned_data.get('idiomas')
        if idiomas.count() < 1:
            raise forms.ValidationError('Por favor, elige al menos un idioma')

        return idiomas

    def clean_genero(self):
        genero = self.cleaned_data.get('genero')
        generos = ['M', 'F', 'O']
        if genero not in generos:
            raise forms.ValidationError('El género debe ser Masculino, Femenino u Otro')

        return genero

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if len(descripcion) > 1000:
            raise forms.ValidationError('La descripción debe contener menos de 1000 caracteres')

        return descripcion

    def clean_lugar(self):
        lugar = self.cleaned_data.get('lugar')
        if len(lugar) > 40:
            raise forms.ValidationError('El lugar debe contener menos de 40 caracteres')
        return lugar


    def clean_piso_encontrado(self):
        piso_encontrado = self.cleaned_data.get('piso_encontrado')
        valores = ['True', 'False']
        if piso_encontrado not in valores:
            raise forms.ValidationError('El valor debe ser Sí o No')

        return piso_encontrado

class ChangePasswordForm(forms.Form):
    password = forms.CharField(required=True,error_messages={'required': 'El campo es obligatorio'},widget=forms.PasswordInput(attrs={'placeholder': 'Nueva contraseña'}))
    password2 = forms.CharField(required=True,error_messages={'required': 'El campo es obligatorio'},widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar nueva contraseña'}))
    
    def clean_password(self):
        password = self.cleaned_data['password']
        regex = re.compile("^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$")
        if not re.fullmatch(regex, password):
            raise forms.ValidationError('La contraseña debe contener como mínimo 8 caracteres, entre ellos una letra y un número')
        return password

    def clean_password2(self):

        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if not password2:
            raise forms.ValidationError('Por favor, confirma tu contraseña')
        if password != password2:
            raise forms.ValidationError('Las contraseñas no coinciden')

        return password2


class ChangePhotoForm(forms.Form):
    foto_usuario = forms.ImageField(label="Foto", error_messages={'required': 'El campo es obligatorio'})
