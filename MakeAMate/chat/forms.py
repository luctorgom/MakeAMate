#encoding:utf-8
from django import forms

class CrearGrupo(forms.Form):
    def __init__(self, user_list, *args, **kwargs):

        super(CrearGrupo, self).__init__(*args, **kwargs)
        self.fields['Personas'] = forms.MultipleChoiceField(
            widget = forms.CheckboxSelectMultiple,
            choices=tuple([(name.id, name) for name in user_list]),
            )
        self.fields['Nombre'].error_messages = {'required': 'Seleccione un nombre para el grupo'}
         
        self.fields['Personas'].error_messages = {'required': 'Seleccione al menos 2 usuarios '}
    Nombre = forms.CharField(widget=forms.TextInput(attrs={'class': 'nombrePartitipante'}))
    Personas = forms.MultipleChoiceField()


    def clean_Personas(self):
        gente = self.cleaned_data.get('Personas')
        if len(gente) < 2:
            raise forms.ValidationError('Debe seleccionar al menos 2 personas')
        return gente