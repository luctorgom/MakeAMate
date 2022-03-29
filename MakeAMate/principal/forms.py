from django import forms
from soupsieve import select
from .models import Tag,Aficiones

class UsuarioForm(forms.Form):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Usuario'}))
    password = forms.CharField(required=True,widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))
    password2 = forms.CharField(required=True,widget=forms.PasswordInput(attrs={'placeholder': 'Confirma la contraseña'}))
    nombre = forms.CharField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Nombre'}))
    apellidos = forms.CharField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Apellidos'}))
    correo = forms.EmailField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Correo Electrónico'}))
    telefono = forms.EmailField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Teléfono'}))
    piso_encontrado = forms.ChoiceField(choices=((True, 'Si'),(False,'No')))
    fecha_nacimiento= forms.DateField(required=True,widget=forms.DateInput(attrs={'placeholder': '01-01-2000'}))
    lugar = forms.CharField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Ciudad de estudios'}))
    nacionalidad = forms.CharField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Nacionalidad'}))
    genero = forms.ChoiceField(choices=(('F', 'Femenino'),('M','Masculino'),('O','Otro')),required=True)
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(),widget=forms.SelectMultiple(attrs={'class': 'select_field_class'}))   
    aficiones = forms.ModelMultipleChoiceField(queryset=Aficiones.objects.all(),required=True,widget=forms.SelectMultiple(attrs={'class': 'select_field_class'}))         
    fotos_usuario = forms.ImageField(label="Fotos")
    zona_piso = forms.CharField(required=True,widget=forms.TextInput(attrs={'class':'zona_piso','placeholder': 'Describe la zona de tu piso'}))
