from django import forms
from .models import Tags,Gustos

class UsuarioForm(forms.Form):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Usuario'}))
    password = forms.CharField(required=True,widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))
    password2 = forms.CharField(required=True,widget=forms.PasswordInput(attrs={'placeholder': 'Confirma la contraseña'}))
    nombre = forms.CharField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Nombre'}))
    apellidos = forms.CharField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Apellidos'}))
    ##descripcion = forms.CharField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Descripción'}))
    correo = forms.EmailField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Correo Electrónico'}))
    piso = forms.ChoiceField(choices=((True, 'Si'),(False,'No')))
    fecha_nacimiento= forms.DateField(required=True,widget=forms.DateInput(attrs={'placeholder': '01-01-2000'}))
    lugar = forms.CharField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Ciudad de estudios'}))
    nacionalidad = forms.CharField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Nacionalidad'}))
    genero = forms.ChoiceField(choices=(('F', 'Femenino'),('M','Masculino'),('O','Otro')),required=True)
    ##pronombres = forms.ChoiceField(choices=(('Ella', 'Ella'),('El','El'),('Elle','Elle')),required=True)   
    ##idiomas = forms.MultipleChoiceField(choices=(('ES', 'Español'),('EN','Inglés'),('FR','Francés'),
          ##                                          ('DE','Alemán'),('PT','Portugués'),('IT','Italiano'),
             ##                                       ('SV','Sueco'),('OT','Otro')),required=True,widget=forms.SelectMultiple())
    ##universidad = forms.CharField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Centro de estudios'}))
    ##estudios = forms.CharField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Estudios'}))
    tags = forms.ModelMultipleChoiceField(queryset=Tags.objects.all(),required=True,widget=forms.SelectMultiple(attrs={'class': 'select_field_class'}))    ##
    gustos = forms.ModelMultipleChoiceField(queryset=Gustos.objects.all(),required=True,widget=forms.SelectMultiple(attrs={'class': 'select_field_class'}))         ##
    ##otras_tags = forms.CharField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Añade otras tags de la siguente forma: amigable,activo,...'}))    ###
    ##otros_gustos = forms.CharField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Añade otros gustos de la siguente forma: amigable,activo,...'}))   ###
    fotos_usuario = forms.FileField(label="Fotos")
    fotos_piso = forms.FileField(label="Fotos de tu piso")
