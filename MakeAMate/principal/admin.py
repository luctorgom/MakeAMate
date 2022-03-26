from django.contrib import admin
from .models import Usuario, Tags, Aficiones, Mates, Idiomas, Ofertas
# Register your models here.
admin.site.register(Usuario)
admin.site.register(Tags)
admin.site.register(Idiomas)
admin.site.register(Aficiones)
admin.site.register(Mates)
admin.site.register(Ofertas)