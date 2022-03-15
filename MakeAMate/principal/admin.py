from django.contrib import admin
from .models import Usuario, Tags, Gustos, Aficiones
# Register your models here.
admin.site.register(Usuario)
admin.site.register(Tags)
admin.site.register(Gustos)
admin.site.register(Aficiones)