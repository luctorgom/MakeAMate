from django.contrib import admin
from .models import Usuario, Tags, Gustos, Aficiones, Mates
# Register your models here.
admin.site.register(Usuario)
admin.site.register(Tags)
admin.site.register(Gustos)
admin.site.register(Aficiones)
admin.site.register(Mates)