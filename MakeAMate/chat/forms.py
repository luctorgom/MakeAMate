#encoding:utf-8
from django import forms

class CrearGrupo(forms.Form):
    def __init__(self, user_list, *args, **kwargs):

        super(CrearGrupo, self).__init__(*args, **kwargs)
        self.fields['Personas'] = forms.MultipleChoiceField(
            widget = forms.CheckboxSelectMultiple,
            choices=tuple([(name.id, name) for name in user_list]),
            )
        self.fields['Nombre'].error_messages = {'required': 'Seleccione un nombre para el grupo no mayor a 30 caracteres'}
         
        self.fields['Personas'].error_messages = {'required': 'Seleccione al menos dos usuarios y no más de 10'}
    Nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'nombrePartitipante'}))
    Personas = forms.MultipleChoiceField()

    def clean_Personas(self):
        gente = self.cleaned_data.get('Personas')
        if len(gente) < 2 or len(gente)>10:
            raise forms.ValidationError('Prueba')
        return gente

    def clean_Nombre(self):
        nombre = self.cleaned_data.get('Nombre')
        if len(nombre) > 40:
            raise forms.ValidationError('Prueba')
        return nombre
