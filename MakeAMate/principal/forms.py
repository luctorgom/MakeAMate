from django import forms
from django.conf import settings

from principal.models import Idiomas, Aficiones, Tags

class UsuarioForm(forms.Form):
    username = forms.CharField(max_length=100, min_length= 5,
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Usuario'}))
    password = forms.CharField(required=True,widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))
    password2 = forms.CharField(required=True,widget=forms.PasswordInput(attrs={'placeholder': 'Confirma la contraseña'}))
    nombre = forms.CharField(required=True,max_length = 150, widget=forms.TextInput(attrs={'placeholder': 'Nombre'}))
    apellidos = forms.CharField(required=True,max_length = 150,widget=forms.TextInput(attrs={'placeholder': 'Apellidos'}))
    correo = forms.EmailField(required=True,widget=forms.TextInput(attrs={'placeholder': 'Correo Electrónico'}))

    piso = forms.ChoiceField(choices=((True, 'Si'),(False,'No')))
    #foto_usuario = forms.ImageField(label="Fotos")
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

    #Validación del formulario
    # def clean(self):
    #     #Se obtienen los datos del formulario
    #     super(UsuarioForm, self).clean()

    #     username = self.cleaned_data.get('username')

    #     if len(username) < 5:
    #         self._errors['username'] = self.error_class([
    #             'El nombre de usuario debe contener 5 caracteres como mínimo'])

    #     if len(username) > 100:
    #         self._errors['username'] = self.error_class([
    #             'El nombre de usuario no puede superar los 100 caracteres'])

    #     password = self.cleaned_data.get('password')
    #     password2 = self.cleaned_data.get('password2')

    #     #Validar que la password sigue un patrón concreto


    #     if password != password2:
    #         self._errors['password2'] = self.error_class(['Las contraseñas no coinciden'])

    #     nombre = self.cleaned_data.get('nombre')
