#encoding:utf-8
from django import forms

class CrearGrupo(forms.Form):
    def __init__(self, user_list, *args, **kwargs):

        super(CrearGrupo, self).__init__(*args, **kwargs)
        self.fields['Grupo'] = forms.MultipleChoiceField(
            widget = forms.CheckboxSelectMultiple,
            choices=tuple([(name.id, name) for name in user_list]),

            )
    Nombre = forms.CharField()
    Grupo = forms.MultipleChoiceField()

    

