from django import forms

from principal.models import Idiomas, Aficiones, Tags

class RegistroForm(forms.Form):

    usuario = forms.CharField(label='Nombre de usuario',max_length=50, required=True)
    contraseña = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    piso = forms.BooleanField(label='¿Tienes piso ya?', required=True, widget=forms.RadioSelect(choices=(('Sí', 'Sí'), ('No', 'No'))))
    foto = forms.ImageField(label='Selecciona una imagen',required=True)
    fecha_nacimiento = forms.DateField(label='¿Cuándo naciste',required=True, widget=forms.DateInput(format=('%d-%m-%Y')))
    lugar = forms.CharField(label='¿Dónde vives?',max_length=40, required=True)
    nacionalidad = forms.CharField(label='¿Dónde naciste?',max_length=20, required=False)
    genero = forms.ChoiceField(label='¿Qué género te representa?',choices=(('F', 'Femenino'),('M','Masculino'),('O','Otro')), required=True)
    pronombres = forms.ChoiceField(label='¿Qué pronombre te representan?',choices=((('Ella', 'Ella'),('El','El'),('Elle','Elle'))))
    universidad = forms.CharField(label='¿En qué universidad estudias?',max_length=40, required=True)
    estudios = forms.CharField(label='¿Qué estudios estás cursando',max_length=40, required=True)
    idiomas = forms.ModelMultipleChoiceField(label='¿Qué idiomas hablas?',queryset=Idiomas.objects.all(), widget=forms.CheckboxSelectMultiple)
    tags = forms.ModelMultipleChoiceField(label='Selecciona unas etiquetas',queryset=Tags.objects.all(), widget=forms.CheckboxSelectMultiple)
    aficiones = forms.ModelMultipleChoiceField(label='¿Qué aficiones tienes?',queryset=Aficiones.objects.all(), widget=forms.CheckboxSelectMultiple)
    
    # Validación del formulario
