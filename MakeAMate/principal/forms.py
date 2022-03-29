from django import forms
from django.conf import settings
from principal.models import Idiomas, Aficiones, Tags
from django.contrib.auth.models import User
import re

class UsuarioForm(forms.Form):
    username = forms.CharField(max_length=100, min_length= 5,
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Usuario'}))
    password = forms.CharField(required=True,widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))
    password2 = forms.CharField(required=True,widget=forms.PasswordInput(attrs={'placeholder': 'Confirma la contraseña'}))
    nombre = forms.CharField(required=True,min_length = 1, max_length = 150, widget=forms.TextInput(attrs={'placeholder': 'Nombre'}))
    apellidos = forms.CharField(required=True, min_length= 1, max_length = 150,widget=forms.TextInput(attrs={'placeholder': 'Apellidos'}))
    correo = forms.EmailField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Correo Electrónico'}))

    piso = forms.ChoiceField(choices=((True, 'Si'),(False,'No')))
    foto_usuario = forms.ImageField(label="Fotos")
    fecha_nacimiento = forms.DateField(required=True,widget=forms.DateInput(attrs={'placeholder': '01-01-2000'}), input_formats=settings.DATE_INPUT_FORMATS)
    lugar = forms.CharField(required=True,max_length=40,widget=forms.TextInput(attrs={'placeholder': 'Ciudad de estudios'}))
    nacionalidad = forms.CharField(required=True,max_length=20,widget=forms.TextInput(attrs={'placeholder': 'Nacionalidad'}))
    genero = forms.ChoiceField(choices=(('F', 'Femenino'),('M','Masculino'),('O','Otro')),required=True)
    idiomas = forms.ModelMultipleChoiceField(queryset=Idiomas.objects.all(), widget=forms.CheckboxSelectMultiple)
    tags = forms.ModelMultipleChoiceField(label='¿Qué etiquetas te definen?',queryset=Tags.objects.all(), widget=forms.CheckboxSelectMultiple)
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
        patron = re.match("^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", password)
        if not patron:
            raise forms.ValidationError('La contraseña debe contener como mínimo 8 caracteres, entre ellos una letra y un número')
        
        return password

    def clean_password2(self):

        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password != password2:
            raise forms.ValidationError('Las contraseñas no coinciden')

        return password2
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if len(nombre) < 1:
            raise forms.ValidationError('El nombre tiene que contener como mínimo un carácter')        

        if len(nombre) > 150:
            raise forms.ValidationError('El nombre debe tener menos de 150 caracteres')

    def clean_apellidos(self):
        apellidos = self.cleaned_data.get('apellidos')
        if len(apellidos) < 1:
            raise forms.ValidationError('Los apellidos tienen que contener como mínimo un carácter')        

        if len(apellidos) > 150:
            raise forms.ValidationError('Los apellidos deben tener menos de 150 caracteres')
